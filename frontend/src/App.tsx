import { useEffect, useState } from "react";
import ChatPage from "./components/ChatPage";
import DocumentsPage from "./components/DocumentsPage";
import TelemetryPage from "./components/TelemetryPage";
import { getTopics } from "./api/client";
import "./App.css";

type Page = "chat" | "documents" | "telemetry";

export default function App() {
  const [page, setPage] = useState<Page>("chat");
  const [topics, setTopics] = useState<string[]>([]);
  const [topic, setTopic] = useState<string>("");

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
          <ChatPage topics={topics} topic={topic} onTopicChange={setTopic} />
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
