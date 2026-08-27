from fastapi import APIRouter

from config import TOPICS

router = APIRouter()


@router.get("/topics")
def list_topics():
    return {"topics": TOPICS}
