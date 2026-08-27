"""SQLite şema ve bağlantı yardımcıları.

Şema, eski (Hafta 2-6) tek tablolu 'documents' yapısından, dosya/pasaj
ayrımı yapan iki tabloya geçer:

  documents     -- yüklenen her kaynak dosya için bir satır (meta veri)
  vector_chunks -- her pasaj/chunk için bir satır (embedding burada)
"""

import sqlite3

from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()

    # Eski (Hafta 2-6) şema 'documents' tablosunu title/content/embedding
    # sütunlarıyla tek tabloda tutuyordu. Yeni şema dosya/pasaj ayrımı
    # yaptığı için uyumsuz; eski tabloyu tespit edip temizliyoruz.
    existing_cols = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(documents)").fetchall()
    }
    if existing_cols and "filename" not in existing_cols:
        conn.executescript("DROP TABLE IF EXISTS vector_chunks; DROP TABLE IF EXISTS documents;")

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            topic TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'processing',
            chunk_count INTEGER NOT NULL DEFAULT 0,
            uploaded_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS vector_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Veritabanı şeması hazır: {DB_PATH}")
