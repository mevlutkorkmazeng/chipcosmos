"""Retrieval sonuçlarını context olarak kullanıp chat modelinden yanıt üretir.

İki yol sunar:
  answer_query()  -- tek seferde tam yanıt (POST /api/query)
  stream_answer() -- SSE için token token üretim (POST /api/query/stream)
"""

from config import (
    CHAT_MAX_TOKENS,
    CHAT_MODEL_ALIAS,
    CONFIDENCE_THRESHOLD,
    LOW_CONFIDENCE_NOTE,
    SYSTEM_PROMPT_TEMPLATE,
)
from services.foundry_client import get_chat_client
from services.retrieval import get_top_chunks


def _build_messages(question: str, chunks) -> list[dict]:
    context = "\n\n".join(f"{title}\n{content}" for title, content, _ in chunks)
    return [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(context=context)},
        {"role": "user", "content": question},
    ]


def _sources_payload(chunks) -> list[dict]:
    return [{"title": title, "content": content, "score": score} for title, content, score in chunks]


def answer_query(question: str, manager, topic: str | None = None) -> dict:
    """Dönen değer: {"answer": str, "sources": [{"title","content","score"}, ...]}"""
    chunks = get_top_chunks(question, manager, k=2, topic=topic)
    messages = _build_messages(question, chunks)

    chat_client = get_chat_client(manager, CHAT_MODEL_ALIAS, CHAT_MAX_TOKENS)
    response = chat_client.complete_chat(messages)
    answer = response.choices[0].message.content

    if chunks and chunks[0][2] < CONFIDENCE_THRESHOLD:
        answer += LOW_CONFIDENCE_NOTE

    return {"answer": answer, "sources": _sources_payload(chunks)}


def stream_answer(question: str, manager, topic: str | None = None):
    """Generator: her adımda bir dict yield eder.

    {"type": "token", "content": "..."}          -- akan metin parçası
    {"type": "done", "sources": [...]}            -- üretim bitti, kaynaklar
    """
    chunks = get_top_chunks(question, manager, k=2, topic=topic)
    messages = _build_messages(question, chunks)

    chat_client = get_chat_client(manager, CHAT_MODEL_ALIAS, CHAT_MAX_TOKENS)

    for stream_chunk in chat_client.complete_streaming_chat(messages):
        if not stream_chunk.choices:
            continue
        delta = stream_chunk.choices[0].delta.content
        if delta:
            yield {"type": "token", "content": delta}

    if chunks and chunks[0][2] < CONFIDENCE_THRESHOLD:
        yield {"type": "token", "content": LOW_CONFIDENCE_NOTE}

    yield {"type": "done", "sources": _sources_payload(chunks)}
