"""
Hafta 2 - Ingest: sample_docs.md pasajlarını embed'leyip SQLite'a yazar.

embed_test.py'deki parse/embed mantığını kullanır; sonucu ekrana yazdırmak
yerine rag.db içindeki 'documents' tablosuna kaydeder.

Çalıştırma:
    python ingest.py
"""

import json
import re
import sqlite3
from pathlib import Path

from foundry_local_sdk import Configuration, FoundryLocalManager

_HERE = Path(__file__).parent
DOCS_PATH = str(_HERE / "sample_docs.md")
DB_PATH = str(_HERE / "rag.db")
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"


def load_passages(path: str) -> list[dict]:
    """sample_docs.md dosyasını '## N. Başlık' bölümlerine ayırır."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"(?m)^## ", content)[1:]
    passages = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        passages.append({"title": title, "content": body})
    return passages


def get_embedding_model(manager: FoundryLocalManager, alias: str):
    """Katalogdan verilen alias'ı bulur; yoksa mevcut ilk embedding modeline düşer."""
    model = manager.catalog.get_model(alias)
    if model is not None:
        return model

    print(f"Uyarı: '{alias}' katalogda bulunamadı, mevcut bir embedding modeli aranıyor...")
    for candidate in manager.catalog.list_models():
        if candidate.info.task == "embeddings":
            print(f"'{candidate.alias}' kullanılacak.")
            return candidate

    raise RuntimeError("Katalogda hiç embedding modeli bulunamadı.")


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )


def main():
    passages = load_passages(DOCS_PATH)
    print(f"{len(passages)} pasaj yüklendi ({DOCS_PATH}).")

    # hello_model.py / embed_test.py ile aynı mimari.
    FoundryLocalManager.initialize(Configuration(app_name="local-rag-assistant"))
    manager = FoundryLocalManager.instance

    model = get_embedding_model(manager, EMBEDDING_MODEL_ALIAS)
    print(f"'{model.alias}' modeli indiriliyor/yükleniyor (ilk çalıştırmada indirme yapabilir)...")
    model.download()
    model.load()

    embedding_client = model.get_embedding_client()

    print("Pasajlar embed ediliyor...")
    texts = [f"{p['title']}\n{p['content']}" for p in passages]
    response = embedding_client.generate_embeddings(texts)

    conn = sqlite3.connect(DB_PATH)
    create_table(conn)
    # Yeniden çalıştırıldığında satırların tekrar tekrar birikmemesi için
    # tabloyu her seferinde baştan doldur.
    conn.execute("DELETE FROM documents")

    for passage, item in zip(passages, response.data):
        embedding_json = json.dumps(item.embedding)
        conn.execute(
            "INSERT INTO documents (title, content, embedding) VALUES (?, ?, ?)",
            (passage["title"], passage["content"], embedding_json),
        )

    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    print(f"\n'{DB_PATH}' -> 'documents' tablosuna toplam {count} satır eklendi.")

    conn.close()


if __name__ == "__main__":
    main()
