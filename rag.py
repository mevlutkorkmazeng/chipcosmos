"""
Hafta 2 - RAG: rag.db'deki pasajları retrieval + local chat modeliyle birleştirir.

get_top_chunks(): sorguyu embed'leyip rag.db'deki pasajlarla cosine similarity
kıyaslar (embed_test.py'deki mantığın SQLite'tan okuyacak hali).
answer_query(): bulunan pasajları context olarak chat modeline (hello_model.py
ile aynı mimari ve max_tokens sınırı) system prompt üzerinden verir.

Çalıştırma:
    python rag.py
"""

import json
import sqlite3
from pathlib import Path

import numpy as np

from foundry_local_sdk import Configuration, FoundryLocalManager

# Script hangi çalışma dizininden başlatılırsa başlatılsın (örn. streamlit run
# başka bir cwd'den çağrıldığında) rag.db'yi bu dosyanın yanında bulsun.
DB_PATH = str(Path(__file__).parent / "rag.db")
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
CHAT_MODEL_ALIAS = "phi-3.5-mini"
CHAT_MAX_TOKENS = 180
# get_top_chunks()'ın en iyi skoru bu eşiğin altındaysa, retrieval'in konuyla
# gerçekten ilgili bir pasaj bulamadığını varsayıp cevaba bir uyarı ekleriz.
CONFIDENCE_THRESHOLD = 0.35
LOW_CONFIDENCE_NOTE = (
    "\n\nNot: Bu konuda dokümanlarımda net bir bilgi bulamadım, en yakın "
    "bulduğum bilgiyi paylaşıyorum ama emin değilim."
)

_manager = None


def get_manager() -> FoundryLocalManager:
    global _manager
    if _manager is None:
        FoundryLocalManager.initialize(Configuration(app_name="local-rag-assistant"))
        _manager = FoundryLocalManager.instance
    return _manager


def get_model(manager: FoundryLocalManager, alias: str, task_hint: str):
    """Katalogdan verilen alias'ı bulur; yoksa aynı görev için mevcut ilk modele düşer."""
    model = manager.catalog.get_model(alias)
    if model is not None:
        return model

    print(f"Uyarı: '{alias}' katalogda bulunamadı, '{task_hint}' görevi için mevcut bir model aranıyor...")
    for candidate in manager.catalog.list_models():
        if candidate.info.task == task_hint:
            print(f"'{candidate.alias}' kullanılacak.")
            return candidate

    raise RuntimeError(f"Katalogda '{task_hint}' görevi için model bulunamadı.")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_top_chunks(query: str, k: int = 2, topic: str | None = None) -> list[tuple[str, str, float]]:
    """rag.db'deki pasajlar arasından query'e en yakın k tanesini döndürür.

    ``topic`` verilirse arama sadece o konudaki pasajlarla sınırlanır
    (örn. "Semiconductors" ya da "Space Exploration"); ``None`` ise tüm
    konular arasında arama yapılır.

    Her eleman bir ``(title, content, similarity_score)`` tuple'ıdır.
    """
    conn = sqlite3.connect(DB_PATH)
    if topic is not None:
        rows = conn.execute(
            "SELECT title, content, embedding FROM documents WHERE topic = ?", (topic,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT title, content, embedding FROM documents").fetchall()
    conn.close()

    if not rows:
        raise RuntimeError(f"'{DB_PATH}' içindeki 'documents' tablosu boş. Önce ingest.py çalıştırın.")

    manager = get_manager()
    embedding_model = get_model(manager, EMBEDDING_MODEL_ALIAS, "embeddings")
    embedding_model.download()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    query_response = embedding_client.generate_embedding(query)
    query_vector = np.array(query_response.data[0].embedding)

    scored = []
    for title, content, embedding_json in rows:
        vector = np.array(json.loads(embedding_json))
        score = cosine_similarity(query_vector, vector)
        scored.append((title, content, score))

    scored.sort(key=lambda item: item[2], reverse=True)
    return scored[:k]


def answer_query(question: str, topic: str | None = None) -> tuple[str, list[tuple[str, float]]]:
    """İlgili pasajları context olarak kullanıp local chat modeline soruyu sorar.

    ``topic`` verilirse retrieval sadece o konudaki pasajlarla sınırlanır.

    Dönen değer: ``(cevap, kaynaklar)``. ``kaynaklar``, cevap için kullanılan
    pasajların ``(title, similarity_score)`` listesidir.
    """
    chunks = get_top_chunks(question, k=2, topic=topic)
    context = "\n\n".join(f"{title}\n{content}" for title, content, _ in chunks)

    manager = get_manager()
    chat_model = get_model(manager, CHAT_MODEL_ALIAS, "chat-completion")
    chat_model.download()
    chat_model.load()
    chat_client = chat_model.get_chat_client()
    # hello_model.py deneyimi: bu makinede CPU üretimi yavaş; sınırsız üretim
    # (varsayılan 2048 token'a kadar) dahili zaman aşımına takılıp iptal edilebiliyor.
    chat_client.settings.max_tokens = CHAT_MAX_TOKENS

    messages = [
        {
            "role": "system",
            "content": (
                "You must answer using ONLY the information in the context below. "
                "If the answer is not explicitly stated in the context, respond with "
                'EXACTLY this and nothing else: "I don\'t know based on the provided '
                "documents.\" Do not use any outside knowledge, even if you know the "
                "answer. When citing context, refer to it by its topic/title only "
                '(e.g. "According to the passage on MOSFETs..."), NEVER by a number '
                'like "passage 1".'
                "\n\nContext:\n" + context
            ),
        },
        {"role": "user", "content": question},
    ]

    response = chat_client.complete_chat(messages)
    answer = response.choices[0].message.content
    if chunks and chunks[0][2] < CONFIDENCE_THRESHOLD:
        answer += LOW_CONFIDENCE_NOTE
    sources = [(title, score) for title, _content, score in chunks]
    return answer, sources


if __name__ == "__main__":
    question = "What is doping?"
    print(f"Soru: {question}\n")

    top_chunks = get_top_chunks(question, k=2)
    print("--- Kullanılan bağlam (top-2) ---")
    for title, _content, score in top_chunks:
        print(f"[{score:.4f}] {title}")

    print("\n--- Model cevabı ---")
    answer, sources = answer_query(question)
    print(answer)
    print("\n--- Kaynaklar ---")
    for title, score in sources:
        print(f"[{score:.4f}] {title}")
