export interface Source {
  title: string;
  content: string;
  score: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  topic?: string;
}

export interface ChatSession {
  id: string;
  createdAt: string;
  messages: ChatMessage[];
}

export interface DocumentRow {
  id: number;
  filename: string;
  topic: string;
  status: "processing" | "indexed" | "failed";
  chunk_count: number;
  uploaded_at: string;
}

export interface Telemetry {
  system: {
    cpu_percent: number;
    cpu_cores: number;
    ram: { used_gb: number; total_gb: number; percent: number };
    disk: { used_gb: number; total_gb: number; percent: number };
  };
  runtime: {
    uptime_seconds: number;
    offline: boolean;
  };
  knowledge_base: {
    document_count: number;
    chunk_count: number;
    by_topic: { topic: string; doc_count: number; chunks: number }[];
    by_status: { status: string; count: number }[];
  };
}
