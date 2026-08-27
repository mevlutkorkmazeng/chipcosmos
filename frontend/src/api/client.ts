import type { DocumentRow, Source, Telemetry } from "../types";

const API_BASE = "http://localhost:8000/api";

async function handleJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `İstek başarısız (${res.status})`);
  }
  return res.json();
}

export async function getTopics(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/topics`);
  const data = await handleJson<{ topics: string[] }>(res);
  return data.topics;
}

export async function getDocuments(): Promise<DocumentRow[]> {
  const res = await fetch(`${API_BASE}/documents`);
  const data = await handleJson<{ documents: DocumentRow[] }>(res);
  return data.documents;
}

export async function uploadDocument(file: File, topic: string) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("topic", topic);
  const res = await fetch(`${API_BASE}/documents`, { method: "POST", body: formData });
  return handleJson<{ filename: string; topic: string; chunk_count: number; status: string }>(res);
}

export async function deleteDocument(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  await handleJson(res);
}

export async function getTelemetry(): Promise<Telemetry> {
  const res = await fetch(`${API_BASE}/telemetry`);
  return handleJson<Telemetry>(res);
}

export async function exportPdf(
  question: string,
  answer: string,
  topic: string,
  sources: Source[]
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      answer,
      topic,
      sources: sources.map((s) => ({ title: s.title, score: s.score })),
    }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `PDF oluşturulamadı (${res.status})`);
  }
  return res.blob();
}

interface StreamCallbacks {
  onToken: (token: string) => void;
  onDone: (sources: Source[]) => void;
  onError: (message: string) => void;
}

/** SSE akışını fetch + ReadableStream ile tüketir (EventSource POST desteklemediği için). */
export async function queryStream(question: string, topic: string, callbacks: StreamCallbacks): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/query/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, topic }),
    });
  } catch {
    callbacks.onError("Backend'e ulaşılamıyor. Sunucunun çalıştığından emin olun (localhost:8000).");
    return;
  }

  if (!res.ok || !res.body) {
    callbacks.onError(`İstek başarısız (${res.status})`);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sepIndex: number;
    while ((sepIndex = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, sepIndex);
      buffer = buffer.slice(sepIndex + 2);
      const line = rawEvent.replace(/^data:\s*/, "");
      if (!line) continue;

      try {
        const event = JSON.parse(line);
        if (event.type === "token") callbacks.onToken(event.content);
        else if (event.type === "done") callbacks.onDone(event.sources);
        else if (event.type === "error") callbacks.onError(event.error);
      } catch {
        // Bozuk/parça halinde JSON gelirse yoksay, sonraki event'te devam eder.
      }
    }
  }
}
