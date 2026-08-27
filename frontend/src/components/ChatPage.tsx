import { useEffect, useRef, useState } from "react";
import { exportPdf, queryStream } from "../api/client";
import type { ChatMessage, ChatSession, Source } from "../types";

interface ChatPageProps {
  topics: string[];
  topic: string;
  onTopicChange: (topic: string) => void;
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  isStreaming: boolean;
  setIsStreaming: React.Dispatch<React.SetStateAction<boolean>>;
  sessions: ChatSession[];
  activeSessionId: string;
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
}

function getSessionTitle(session: ChatSession): string {
  const firstUserMessage = session.messages.find((m) => m.role === "user");
  if (!firstUserMessage || !firstUserMessage.content.trim()) return "Yeni Sohbet";
  const text = firstUserMessage.content.trim();
  return text.length > 36 ? text.slice(0, 36) + "…" : text;
}

function SessionList({
  sessions,
  activeSessionId,
  onNewSession,
  onSelectSession,
  onDeleteSession,
}: {
  sessions: ChatSession[];
  activeSessionId: string;
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
}) {
  return (
    <aside className="chat-sessions">
      <button className="new-session-btn" onClick={onNewSession}>
        + Yeni Sohbet
      </button>
      <div className="session-list">
        {sessions.map((s) => (
          <div key={s.id} className={`session-item ${s.id === activeSessionId ? "active" : ""}`}>
            <button className="session-select" onClick={() => onSelectSession(s.id)}>
              {getSessionTitle(s)}
            </button>
            <button
              className="session-delete"
              title="Sohbeti sil"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(s.id);
              }}
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}

function SourceList({ sources }: { sources: Source[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="sources">
      <button className="sources-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? "▾" : "▸"} Kullanılan kaynaklar ({sources.length})
      </button>
      {open && (
        <div className="sources-list">
          {sources.map((s, i) => (
            <div key={i} className="source-card">
              <div className="source-title">{s.title}</div>
              <div className="source-score">Retrieved: score {s.score.toFixed(2)}</div>
              <div className="source-content">{s.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ExportPdfButton({
  question,
  answer,
  topic,
  sources,
}: {
  question: string;
  answer: string;
  topic: string;
  sources: Source[];
}) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleExport() {
    setIsExporting(true);
    setError(null);
    try {
      const blob = await exportPdf(question, answer, topic, sources);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "rag-report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <span className="export-pdf">
      <button className="export-pdf-btn" onClick={handleExport} disabled={isExporting}>
        {isExporting ? "Hazırlanıyor..." : "📄 Export PDF"}
      </button>
      {error && <span className="export-pdf-error">⚠️ {error}</span>}
    </span>
  );
}

export default function ChatPage({
  topics,
  topic,
  onTopicChange,
  messages,
  setMessages,
  isStreaming,
  setIsStreaming,
  sessions,
  activeSessionId,
  onNewSession,
  onSelectSession,
  onDeleteSession,
}: ChatPageProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isStreaming) return;

    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", topic },
    ]);
    setIsStreaming(true);

    await queryStream(question, topic, {
      onToken: (token) => {
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            ...next[next.length - 1],
            content: next[next.length - 1].content + token,
          };
          return next;
        });
      },
      onDone: (sources) => {
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { ...next[next.length - 1], sources };
          return next;
        });
        setIsStreaming(false);
      },
      onError: (message) => {
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            ...next[next.length - 1],
            content: next[next.length - 1].content || `⚠️ Hata: ${message}`,
          };
          return next;
        });
        setIsStreaming(false);
      },
    });
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div>
          <h1>🚀 ChipCosmos</h1>
          <p className="subtitle">
            Yarı iletkenler ve uzay araştırmaları için yerel, kaynak gösteren bir RAG asistanı — Microsoft
            Foundry Local ile %100 çevrimdışı.
          </p>
        </div>
        <label className="topic-select">
          Konu:
          <select value={topic} onChange={(e) => onTopicChange(e.target.value)}>
            {topics.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="chat-body">
        <SessionList
          sessions={sessions}
          activeSessionId={activeSessionId}
          onNewSession={onNewSession}
          onSelectSession={onSelectSession}
          onDeleteSession={onDeleteSession}
        />

        <div className="chat-main">
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">💬</div>
                <h2>Bugün size nasıl yardımcı olabilirim?</h2>
                <p>Seçili konu hakkında bir soru sorun — cevaplar sadece indekslenmiş dokümanlara dayanır.</p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <div className="message-role">{msg.role === "user" ? "🧑 Siz" : "🤖 Asistan"}</div>
                {msg.role === "assistant" && msg.topic && <div className="message-topic">Konu: {msg.topic}</div>}
                <div className="message-content">
                  {msg.content || (isStreaming && i === messages.length - 1 ? "▍" : "")}
                </div>
                {msg.sources && (
                  <div className="message-footer">
                    <SourceList sources={msg.sources} />
                    <ExportPdfButton
                      question={messages[i - 1]?.content ?? ""}
                      answer={msg.content}
                      topic={msg.topic ?? topic}
                      sources={msg.sources}
                    />
                  </div>
                )}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="chat-input-row">
            <textarea
              placeholder="Sorunuzu yazın..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isStreaming}
            />
            <button onClick={handleSend} disabled={isStreaming || !input.trim()}>
              {isStreaming ? "..." : "Gönder"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
