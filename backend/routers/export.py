from fastapi import APIRouter, Response
from pydantic import BaseModel

from services.pdf_export import build_pdf

router = APIRouter()


class SourceIn(BaseModel):
    title: str
    score: float


class ExportPdfRequest(BaseModel):
    question: str
    answer: str
    topic: str
    sources: list[SourceIn] = []


@router.post("/export/pdf")
def export_pdf(req: ExportPdfRequest):
    pdf_bytes = build_pdf(
        question=req.question,
        answer=req.answer,
        topic=req.topic,
        sources=[s.model_dump() for s in req.sources],
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="rag-report.pdf"'},
    )
