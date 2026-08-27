import { useEffect, useState } from "react";
import ChatPage from "./components/ChatPage";
import DocumentsPage from "./components/DocumentsPage";
import TelemetryPage from "./components/TelemetryPage";
import { getTopics } from "./api/client";
import type { ChatMessage, ChatSession } from "./types";
import "./App.css";

type Page = "chat" | "documents" | "telemetry";

const SESSIONS_STORAGE_KEY = "chipcosmos:sessions";
const ACTIVE_SESSION_STORAGE_KEY = "chipcosmos:activeSessionId";
const LEGACY_MESSAGES_STORAGE_KEY = "chipcosmos:messages"; // eski (oturumsuz) format

function createEmptySession(): ChatSession {
  return { id: crypto.randomUUID(), createdAt: new Date().toISOString(), messages: [] };
}

/** localStorage'dan oturumları okur; hiç yoksa eski (Hafta 6) tekli-sohbet
 * formatından migrate eder; o da yoksa boş bir oturumla başlar. */
function loadInitialSessions(): ChatSession[] {
  try {
    const saved = localStorage.getItem(SESSIONS_STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved) as ChatSession[];
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch {
    // bozuk veri - yoksay, aşağıdaki fallback'lere düş
  }

  try {
    const legacy = localStorage.getItem(LEGACY_MESSAGES_STORAGE_KEY);
    if (legacy) {
      const messages = JSON.parse(legacy) as ChatMessage[];
      if (Array.isArray(messages) && messages.length > 0) {
        return [{ id: crypto.randomUUID(), createdAt: new Date().toISOString(), messages }];
      }
    }
  } catch {
    // yoksay
  }

  return [createEmptySession()];
}

export default function App() {
  const [page, setPage] = useState<Page>("chat");
  const [topics, setTopics] = useState<string[]>([]);
  const [topic, setTopic] = useState<string>("");

  // Sohbet oturumları (ChatGPT tarzı): birden fazla ayrı sohbet, biri aktif.
  // Hem üst seviyede (sayfa değiştirince ChatPage unmount olsa bile
  // kaybolmasın diye) hem localStorage'da (F5/sekme kapat-aç'ta kaybolmasın
  // diye) tutuluyor.
  const [sessions, setSessions] = useState<ChatSession[]>(loadInitialSessions);
  const [activeSessionId, setActiveSessionId] = useState<string>(() => {
    const initial = loadInitialSessions();
    try {
      const saved = localStorage.getItem(ACTIVE_SESSION_STORAGE_KEY);
      if (saved && initial.some((s) => s.id === saved)) return saved;
    } catch {
      // yoksay
    }
    return initial[0].id;
  });
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(sessions));
    } catch {
      // localStorage dolu/erişilemez olabilir - sessizce yoksay
    }
  }, [sessions]);

  useEffect(() => {
    try {
      localStorage.setItem(ACTIVE_SESSION_STORAGE_KEY, activeSessionId);
    } catch {
      // yoksay
    }
  }, [activeSessionId]);

  useEffect(() => {
    getTopics()
      .then((t) => {
        setTopics(t);
        if (t.length > 0) setTopic(t[0]);
      })
      .catch(() => {
        // Backend henüz ayakta değilse boş bırak; kullanıcı sunucuyu başlatınca sayfa yenilenebilir.
      });
  }, []);

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? sessions[0];
  const messages = activeSession?.messages ?? [];

  // ChatPage'e React'in normal setState imzasıyla (değer ya da updater
  // fonksiyonu) geçiliyor, ama arkada aktif oturumun mesajlarını güncelliyor.
  const setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>> = (update) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== activeSessionId) return s;
        const nextMessages = typeof update === "function" ? (update as (p: ChatMessage[]) => ChatMessage[])(s.messages) : update;
        return { ...s, messages: nextMessages };
      })
    );
  };

  function handleNewSession() {
    const fresh = createEmptySession();
    setSessions((prev) => [fresh, ...prev]);
    setActiveSessionId(fresh.id);
  }

  function handleSelectSession(id: string) {
    setActiveSessionId(id);
  }

  function handleDeleteSession(id: string) {
    const remaining = sessions.filter((s) => s.id !== id);
    if (remaining.length === 0) {
      const fresh = createEmptySession();
      setSessions([fresh]);
      setActiveSessionId(fresh.id);
      return;
    }
    setSessions(remaining);
    if (activeSessionId === id) {
      setActiveSessionId(remaining[0].id);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img src="/chipcosmos-icon.png" alt="ChipCosmos" className="brand-icon" />
          <div>
            <div className="brand-name">ChipCosmos</div>
            <div className="brand-sub">Control Center</div>
          </div>
        </div>

        <nav>
          <button className={page === "chat" ? "active" : ""} onClick={() => setPage("chat")}>
            💬 Sohbet
          </button>
          <button className={page === "documents" ? "active" : ""} onClick={() => setPage("documents")}>
            📄 Dokümanlar
          </button>
          <button className={page === "telemetry" ? "active" : ""} onClick={() => setPage("telemetry")}>
            📊 Telemetri
          </button>
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" /> 100% Offline · Foundry Local
        </div>
      </aside>

      <main className="main-content">
        {page === "chat" && topics.length > 0 && (
          <ChatPage
            topics={topics}
            topic={topic}
            onTopicChange={setTopic}
            messages={messages}
            setMessages={setMessages}
            isStreaming={isStreaming}
            setIsStreaming={setIsStreaming}
            sessions={sessions}
            activeSessionId={activeSessionId}
            onNewSession={handleNewSession}
            onSelectSession={handleSelectSession}
            onDeleteSession={handleDeleteSession}
          />
        )}
        {page === "documents" && <DocumentsPage topics={topics.length > 0 ? topics : ["Semiconductors"]} />}
        {page === "telemetry" && <TelemetryPage />}
        {page === "chat" && topics.length === 0 && (
          <div className="loading-state">Backend'e bağlanılıyor... (localhost:8000 çalışıyor mu?)</div>
        )}
      </main>
    </div>
  );
}
