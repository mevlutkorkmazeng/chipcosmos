import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import TOPICS
from services.foundry_client import get_manager
from services.generation import answer_query, stream_answer
from services.sanitize import is_blank, sanitize_query

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    topic: str | None = None


def _validate_topic(topic: str | None) -> None:
    if topic is not None and topic not in TOPICS:
        raise HTTPException(400, f"Geçersiz konu: {topic}. Geçerli değerler: {TOPICS}")


def _clean_question(raw_question: str) -> str:
    question = sanitize_query(raw_question)
    if is_blank(question):
        raise HTTPException(400, "Soru boş olamaz.")
    return question


@router.post("/query")
def query(req: QueryRequest):
    _validate_topic(req.topic)
    question = _clean_question(req.question)
    manager = get_manager()
    try:
        return answer_query(question, manager, topic=req.topic)
    except RuntimeError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/query/stream")
def query_stream(req: QueryRequest):
    _validate_topic(req.topic)
    question = _clean_question(req.question)
    manager = get_manager()

    def event_generator():
        try:
            for event in stream_answer(question, manager, topic=req.topic):
                yield f"data: {json.dumps(event)}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
