from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, TOPICS, UPLOAD_DIR
from db import get_connection
from services.foundry_client import get_manager
from services.ingestion import ingest_file

router = APIRouter()


@router.get("/documents")
def list_documents():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, filename, topic, status, chunk_count, uploaded_at "
        "FROM documents ORDER BY uploaded_at DESC"
    ).fetchall()
    conn.close()
    return {"documents": [dict(row) for row in rows]}


@router.post("/documents")
async def upload_document(file: UploadFile = File(...), topic: str = Form(...)):
    if topic not in TOPICS:
        raise HTTPException(400, f"Geçersiz konu: {topic}. Geçerli değerler: {TOPICS}")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400, f"Desteklenmeyen dosya türü: {ext}. İzin verilenler: {sorted(ALLOWED_EXTENSIONS)}"
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(400, f"Dosya çok büyük (limit {MAX_UPLOAD_MB}MB).")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Path traversal koruması: sadece dosya adını (basename) kullan.
    safe_name = Path(file.filename).name
    dest = UPLOAD_DIR / safe_name
    dest.write_bytes(contents)

    manager = get_manager()
    try:
        chunk_count = ingest_file(str(dest), safe_name, topic, manager)
    except Exception as exc:
        raise HTTPException(500, f"İşleme hatası: {exc}") from exc

    return {"filename": safe_name, "topic": topic, "chunk_count": chunk_count, "status": "indexed"}


@router.delete("/documents/{document_id}")
def delete_document(document_id: int):
    conn = get_connection()
    row = conn.execute("SELECT id FROM documents WHERE id = ?", (document_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(404, "Doküman bulunamadı.")
    conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    return {"deleted": document_id}
