import { useEffect, useState } from "react";
import { getTelemetry } from "../api/client";
import type { Telemetry } from "../types";

const REFRESH_MS = 5000;

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}s ${m}dk ${s}sn`;
  if (m > 0) return `${m}dk ${s}sn`;
  return `${s}sn`;
}

function UsageBar({ label, percent, detail }: { label: string; percent: number; detail: string }) {
  const level = percent > 85 ? "high" : percent > 60 ? "medium" : "low";
  return (
    <div className="usage-card">
      <div className="usage-header">
        <span>{label}</span>
        <span className="usage-percent">%{percent.toFixed(1)}</span>
      </div>
      <div className="usage-track">
        <div className={`usage-fill usage-${level}`} style={{ width: `${Math.min(percent, 100)}%` }} />
      </div>
      <div className="usage-detail">{detail}</div>
    </div>
  );
}

export default function TelemetryPage() {
  const [data, setData] = useState<Telemetry | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchTelemetry() {
      try {
        const result = await getTelemetry();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    }

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="telemetry-page">
      <h1>📊 Sistem Telemetrisi</h1>
      <p className="subtitle">
        Bu iş istasyonunun sistem durumu ve bilgi tabanı istatistikleri — {REFRESH_MS / 1000} saniyede bir
        güncellenir.
      </p>

      {error && <div className="error-banner">⚠️ {error} — backend çalışıyor mu? (localhost:8000)</div>}

      {data && (
        <>
          <div className="usage-grid">
            <UsageBar
              label="CPU"
              percent={data.system.cpu_percent}
              detail={`${data.system.cpu_cores} çekirdek`}
            />
            <UsageBar
              label="RAM"
              percent={data.system.ram.percent}
              detail={`${data.system.ram.used_gb} / ${data.system.ram.total_gb} GB`}
            />
            <UsageBar
              label="Disk"
              percent={data.system.disk.percent}
              detail={`${data.system.disk.used_gb} / ${data.system.disk.total_gb} GB`}
            />
          </div>

          <div className="telemetry-row">
            <div className="info-card">
              <div className="info-label">Çalışma süresi (backend)</div>
              <div className="info-value">{formatUptime(data.runtime.uptime_seconds)}</div>
            </div>
            <div className="info-card">
              <div className="info-label">Bağlantı modu</div>
              <div className="info-value">
                <span className="offline-badge">🔒 100% Offline</span>
              </div>
            </div>
            <div className="info-card">
              <div className="info-label">Toplam doküman / chunk</div>
              <div className="info-value">
                {data.knowledge_base.document_count} doküman · {data.knowledge_base.chunk_count} chunk
              </div>
            </div>
          </div>

          <h2 className="section-title">Konuya göre bilgi tabanı</h2>
          <table className="documents-table">
            <thead>
              <tr>
                <th>Konu</th>
                <th>Doküman</th>
                <th>Chunk</th>
              </tr>
            </thead>
            <tbody>
              {data.knowledge_base.by_topic.map((row) => (
                <tr key={row.topic}>
                  <td>{row.topic}</td>
                  <td>{row.doc_count}</td>
                  <td>{row.chunks}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
