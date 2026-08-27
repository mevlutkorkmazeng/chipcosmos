"""Cosine similarity ile SQLite'daki vector_chunks üzerinde retrieval."""

import json

import numpy as np

from config import EMBEDDING_MODEL_ALIAS
from db import get_connection
from services.foundry_client import get_embedding_client


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_top_chunks(
    query: str, manager, k: int = 2, topic: str | None = None
) -> list[tuple[str, str, float]]:
    """En yakın k pasajı döndürür: ``(title, content, similarity_score)``.

    ``topic`` verilirse sadece o konudaki (ve başarıyla indekslenmiş)
    dokümanların pasajları arasında arama yapılır.
    """
    conn = get_connection()
    if topic is not None:
        rows = conn.execute(
            """
            SELECT vc.title, vc.content, vc.embedding
            FROM vector_chunks vc
            JOIN documents d ON d.id = vc.document_id
            WHERE d.topic = ? AND d.status = 'indexed'
            """,
            (topic,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT vc.title, vc.content, vc.embedding
            FROM vector_chunks vc
            JOIN documents d ON d.id = vc.document_id
            WHERE d.status = 'indexed'
            """
        ).fetchall()
    conn.close()

    if not rows:
        raise RuntimeError("İndekslenmiş doküman bulunamadı. Önce belge yükleyin/işleyin.")

    embedding_client = get_embedding_client(manager, EMBEDDING_MODEL_ALIAS)
    query_response = embedding_client.generate_embedding(query)
    query_vector = np.array(query_response.data[0].embedding)

    scored = []
    for row in rows:
        vector = np.array(json.loads(row["embedding"]))
        score = cosine_similarity(query_vector, vector)
        scored.append((row["title"], row["content"], score))

    scored.sort(key=lambda item: item[2], reverse=True)
    return scored[:k]
