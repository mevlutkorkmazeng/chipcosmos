"""Doküman ayrıştırma, parçalama (chunking) ve embedding + DB'ye yazma.

Desteklenen formatlar: .md, .txt, .pdf, .docx

.md/.txt dosyaları '## N. Başlık' formatındaysa (sample_docs.md gibi) o
başlıklara göre bölünür; değilse (ve pdf/docx için her zaman) paragraf
bazlı sabit boyutlu chunking'e düşülür.
"""

import json
import re
from pathlib import Path

from db import get_connection
from services.foundry_client import get_embedding_client

CHUNK_SIZE = 800  # karakter, sabit boyutlu chunking için hedef üst sınır


def _load_markdown_headings(text: str) -> list[dict]:
    sections = re.split(r"(?m)^## ", text)[1:]
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


def _chunk_plain_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[dict]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    buffer = ""
    for para in paragraphs:
        if buffer and len(buffer) + len(para) + 2 > chunk_size:
            chunks.append(buffer.strip())
            buffer = para
        else:
            buffer = f"{buffer}\n\n{para}".strip() if buffer else para
    if buffer:
        chunks.append(buffer.strip())

    return [{"title": f"Chunk {i + 1}", "content": chunk} for i, chunk in enumerate(chunks)]


def _extract_pdf_text(path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx_text(path: str) -> str:
    import docx

    document = docx.Document(path)
    return "\n\n".join(p.text for p in document.paragraphs if p.text.strip())


def load_passages(path: str) -> list[dict]:
    """Bir dosyayı '(title, content)' pasajlarına ayırır."""
    ext = Path(path).suffix.lower()

    if ext in (".md", ".txt"):
        text = Path(path).read_text(encoding="utf-8")
        if re.search(r"(?m)^## ", text):
            return _load_markdown_headings(text)
        return _chunk_plain_text(text)

    if ext == ".pdf":
        return _chunk_plain_text(_extract_pdf_text(path))

    if ext == ".docx":
        return _chunk_plain_text(_extract_docx_text(path))

    raise ValueError(f"Desteklenmeyen dosya türü: {ext}")


def ingest_file(path: str, filename: str, topic: str, manager) -> int:
    """Bir dosyayı embed'leyip 'documents' + 'vector_chunks' tablolarına yazar.

    Dönen değer: eklenen chunk sayısı. Hata olursa 'documents' satırı
    status='failed' olarak işaretlenir ve exception yeniden fırlatılır.
    """
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO documents (filename, topic, status) VALUES (?, ?, 'processing')",
        (filename, topic),
    )
    document_id = cursor.lastrowid
    conn.commit()

    try:
        passages = load_passages(path)
        if not passages:
            raise ValueError("Dosyadan hiç pasaj çıkarılamadı (boş içerik).")

        from config import EMBEDDING_MODEL_ALIAS

        embedding_client = get_embedding_client(manager, EMBEDDING_MODEL_ALIAS)
        texts = [f"{p['title']}\n{p['content']}" for p in passages]
        response = embedding_client.generate_embeddings(texts)

        for i, (passage, item) in enumerate(zip(passages, response.data)):
            embedding_json = json.dumps(item.embedding)
            conn.execute(
                "INSERT INTO vector_chunks (document_id, chunk_index, title, content, embedding) "
                "VALUES (?, ?, ?, ?, ?)",
                (document_id, i, passage["title"], passage["content"], embedding_json),
            )

        conn.execute(
            "UPDATE documents SET status = 'indexed', chunk_count = ? WHERE id = ?",
            (len(passages), document_id),
        )
        conn.commit()
        return len(passages)
    except Exception:
        conn.execute("UPDATE documents SET status = 'failed' WHERE id = ?", (document_id,))
        conn.commit()
        raise
    finally:
        conn.close()
