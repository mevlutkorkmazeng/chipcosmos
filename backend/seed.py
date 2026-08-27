"""Mevcut sample_docs.md ve space_exploration_docs.md dosyalarını yeni
şemaya (documents + vector_chunks) göre rag.db'ye yükler.

Çalıştırma (backend/ klasöründen):
    python seed.py
"""

from pathlib import Path

from db import get_connection, init_db
from services.foundry_client import get_manager
from services.ingestion import ingest_file

_PROJECT_DIR = Path(__file__).parent.parent

SOURCES = [
    (str(_PROJECT_DIR / "sample_docs.md"), "Semiconductors"),
    (str(_PROJECT_DIR / "space_exploration_docs.md"), "Space Exploration"),
]


def main():
    init_db()

    # Yeniden çalıştırıldığında tekrar tekrar birikmesin diye tabloları temizle.
    conn = get_connection()
    conn.execute("DELETE FROM vector_chunks")
    conn.execute("DELETE FROM documents")
    conn.commit()
    conn.close()

    manager = get_manager()

    for path, topic in SOURCES:
        filename = Path(path).name
        print(f"'{filename}' işleniyor -> konu: '{topic}'...")
        chunk_count = ingest_file(path, filename, topic, manager)
        print(f"  -> {chunk_count} chunk eklendi.")

    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM vector_chunks").fetchone()[0]
    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()
    print(f"\nToplam: {doc_count} doküman, {total} chunk.")


if __name__ == "__main__":
    main()
