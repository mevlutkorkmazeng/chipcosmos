import { useEffect, useRef, useState } from "react";
import { deleteDocument, getDocuments, uploadDocument } from "../api/client";
import type { DocumentRow } from "../types";

interface DocumentsPageProps {
  topics: string[];
}

const STATUS_LABEL: Record<string, string> = {
  indexed: "İndekslendi",
  processing: "İşleniyor",
  failed: "Başarısız",
};

export default function DocumentsPage({ topics }: DocumentsPageProps) {
  const [documents, setDocuments] = useState<DocumentRow[]>([]);
  const [uploadTopic, setUploadTopic] = useState(topics[0] ?? "");
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function refresh() {
    try {
      setDocuments(await getDocuments());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setError(null);
    setIsUploading(true);
    for (const file of Array.from(files)) {
      try {
        await uploadDocument(file, uploadTopic);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    }
    setIsUploading(false);
    await refresh();
  }

  async function handleDelete(id: number) {
    await deleteDocument(id);
    await refresh();
  }

  return (
    <div className="documents-page">
      <h1>📄 Doküman Yönetimi</h1>
      <p className="subtitle">Konu için belge yükleyin, işleyin ve yönetin (SQLite vektör indeksi).</p>

      <label
        className={`dropzone ${isDragOver ? "drag-over" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.pdf,.docx"
          multiple
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="dropzone-icon">⬆️</div>
        <div>
          <strong>Dosyaları buraya sürükleyin ya da tıklayıp seçin</strong>
          <div className="dropzone-hint">.txt, .md, .pdf, .docx destekleniyor (max 50MB)</div>
        </div>
      </label>

      <div className="upload-topic-row">
        <label>
          Konu:
          <select value={uploadTopic} onChange={(e) => setUploadTopic(e.target.value)}>
            {topics.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        {isUploading && <span className="uploading-note">Yükleniyor / işleniyor...</span>}
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      <table className="documents-table">
        <thead>
          <tr>
            <th>Dosya adı</th>
            <th>Konu</th>
            <th>Durum</th>
            <th>Chunk</th>
            <th>Yüklenme tarihi</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>{doc.filename}</td>
              <td>{doc.topic}</td>
              <td>
                <span className={`status-badge status-${doc.status}`}>
                  {STATUS_LABEL[doc.status] ?? doc.status}
                </span>
              </td>
              <td>{doc.chunk_count}</td>
              <td>{doc.uploaded_at}</td>
              <td>
                <button className="delete-btn" onClick={() => handleDelete(doc.id)}>
                  Sil
                </button>
              </td>
            </tr>
          ))}
          {documents.length === 0 && (
            <tr>
              <td colSpan={6} className="empty-row">
                Henüz doküman yok.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
