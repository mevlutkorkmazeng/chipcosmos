# ChipCosmos

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A fully offline Retrieval-Augmented Generation (RAG) Q&A assistant, built
on **Microsoft Foundry Local**. It answers questions across multiple
knowledge bases (semiconductors, space exploration) by retrieving relevant
passages and grounding the LLM's answer in that context — with no internet
connection required after setup.

Built as a one-month learning project following the plan in
"One-Month Project Plan: Local RAG AI Assistant with Microsoft Foundry Local".

**Current version: FastAPI backend + React (TypeScript) frontend**, with
streaming responses, per-source similarity/confidence scores, and a
document-management UI for uploading `.txt/.md/.pdf/.docx` files. The
original single-file Streamlit version (`app.py`, `rag.py`, `ingest.py`)
is kept in the repo as the earlier, simpler iteration — see the
"Legacy Streamlit version" section near the bottom of this file.

---

## What it does

Ask a question in the chat interface (e.g. *"What is a MOSFET?"*), and the system:

1. Embeds your question using a local embedding model (`qwen3-embedding-0.6b`)
2. Finds the most relevant passage(s) from a 15-passage knowledge base (stored in SQLite) using cosine similarity
3. Sends your question + the retrieved passage(s) to a local chat model (`phi-3.5-mini`)
4. Returns an answer grounded in the retrieved text, citing which passage it came from (e.g. *"According to passage 11..."*)
5. Explicitly says *"I don't know based on the provided documents"* if the answer isn't in the knowledge base, instead of guessing

The interface keeps a running chat history, and shows exactly which
passage(s) and similarity score were used for each answer — so the
retrieval step is never a "black box."

---

## Architecture

```
 User question (browser)
        │
        ▼
  React frontend (frontend/, Vite + TypeScript, localhost:5173)
        │  fetch() + SSE stream
        ▼
  FastAPI backend (backend/, localhost:8000)
        │
        ├── GET  /api/topics       -- available knowledge-base topics
        ├── GET  /api/documents    -- list uploaded/indexed documents
        ├── POST /api/documents    -- upload + ingest a .txt/.md/.pdf/.docx file
        ├── POST /api/query        -- one-shot Q&A (answer + sources)
        └── POST /api/query/stream -- same, streamed token-by-token (SSE)
        │
        ▼
  services/retrieval.py: get_top_chunks() ── embeds query, compares
        │   against stored embeddings in rag.db (SQLite: documents +
        │   vector_chunks tables), returns (title, content, score)
        ▼
  services/generation.py: answer_query() / stream_answer() ── sends
        │   question + passages to phi-3.5-mini via Foundry Local, with
        │   a system prompt restricting it to the given context and
        │   citing the passage by title (never by number)
        ▼
  Answer (grounded in context, cited, or an explicit refusal) + sources
        │
        ▼
  Displayed in chat, streaming live, with a "Kullanılan kaynaklar"
  panel showing each source's title, similarity score, and full text
```

Everything — the embedding model, the chat model, and the database — runs
**on this one machine**. Nothing is sent to the cloud, to Anthropic, or to
any external service. Foundry Local, FastAPI, Vite, and SQLite are all
local processes with no built-in connection to any AI assistant account.

---

## Security & access model

This project runs as two **local development servers**, not a hosted website.

- **Where it runs:** entirely on this computer, as two local processes —
  the FastAPI backend (`uvicorn`, port 8000) and the Vite dev server
  serving the React frontend (port 5173). No cloud hosting, no external
  server, no deployment anywhere.
- **Who can reach it:** both processes bind to `localhost` only (Vite's
  default; FastAPI's CORS is restricted to `http://localhost:5173`), so
  **only this computer** can open it — not even other devices on the
  same Wi-Fi network.
- **No internet exposure:** nobody outside this local machine can reach
  the app under any circumstances — no port forwarding, tunnel, or
  public hosting is involved.
- **When the computer is off:** the server cannot run, so the app is
  completely unreachable — it is only "live" while the terminal window
  running it is open and the computer is on.
- **Full control:** closing the terminal (or `Ctrl+C`) stops the server
  immediately.
- **No file-system exposure:** visitors can only submit a question
  through the chat box. The application only ever passes that text to
  the RAG pipeline (`answer_query()`) — it does not read, write, or
  expose any file, folder, or other project on this machine, and has
  no connection to any Claude/Anthropic account.
- **Worst case under heavy use:** CPU load increases and responses
  slow down (inference runs on CPU) — there is no data-access risk.

---

## Project files

| Path | Purpose |
|---|---|
| `sample_docs.md`, `space_exploration_docs.md` | Seed knowledge bases — 15 + 10 passages across two topics |
| `hello_model.py` | Week 1 — verifies Foundry Local installation with a basic chat completion |
| `backend/main.py` | FastAPI app: CORS, router registration, `/api/health` |
| `backend/config.py` | Model aliases, confidence threshold, topics, upload limits |
| `backend/db.py` | SQLite schema (`documents` + `vector_chunks`) and migration from the old schema |
| `backend/seed.py` | Loads `sample_docs.md` / `space_exploration_docs.md` into `rag.db` on first run |
| `backend/services/ingestion.py` | Parses `.txt/.md/.pdf/.docx`, chunks, embeds, writes to SQLite |
| `backend/services/retrieval.py` | `get_top_chunks()` — cosine similarity search, optional topic filter |
| `backend/services/generation.py` | `answer_query()` / `stream_answer()` — chat completion + citation prompt |
| `backend/services/pdf_export.py` | Builds the branded PDF report (reportlab) |
| `backend/services/sanitize.py` | Query sanitization + prompt-injection redaction |
| `backend/routers/` | `topics.py`, `documents.py` (list/upload/delete), `query.py` (sync + SSE stream), `export.py` (PDF), `telemetry.py` (system stats) |
| `frontend/src/App.tsx` | Sidebar navigation (Chat / Documents / Telemetri), topic state |
| `frontend/src/components/ChatPage.tsx` | Streaming chat UI with expandable per-source score/content panel + PDF export button |
| `frontend/src/components/DocumentsPage.tsx` | Drag-and-drop upload, document status table |
| `frontend/src/components/TelemetryPage.tsx` | Live CPU/RAM/disk usage, uptime, knowledge-base stats |
| `frontend/src/api/client.ts` | Typed `fetch` wrapper, including SSE stream parsing |
| `app.py`, `rag.py`, `ingest.py` | **Legacy** Streamlit version — see bottom of this file |
| `test_queries.py` | Automated test suite (20 questions: 15 answerable, 5 out-of-scope) — calls the FastAPI backend over HTTP (`POST /api/query`) |

---

## Setup & running (Windows)

Two servers run side by side: the FastAPI backend and the React frontend.

**1. Backend**

```powershell
cd local-rag-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r backend\requirements.txt

# One-time: install the Foundry Local runtime if not already present
winget install Microsoft.FoundryLocal

cd backend

# One-time (or after editing the seed .md files): build the knowledge base
python seed.py

# Launch the API (bound to localhost only)
uvicorn main:app --reload --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

**2. Frontend** (separate terminal)

```powershell
cd local-rag-assistant\frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

---

## Test results (Week 5)

An automated test suite (`test_queries.py`) ran 20 questions against the
assistant: one answerable question per knowledge-base passage (15 total),
and 5 deliberately out-of-scope questions spanning different topics
(geography, biology, math, sports, history). Originally run against
`rag.py` directly; re-run later over HTTP against the FastAPI backend
(`POST /api/query`) with identical results.

| Metric | Result |
|---|---|
| Answerable questions correctly answered, with correct passage retrieved | 15 / 15 |
| Out-of-scope questions correctly refused | 5 / 5 |
| Confidence-threshold note (score < 0.35) attached on all 5 refusals | 5 / 5 |

Retrieval was reliable even on its weakest match: the lowest similarity
score across all 15 answerable questions was still 0.52, and it still
pointed to the correct passage.

**Two things worth noting honestly, rather than hiding them:**

1. In one of the 5 out-of-scope questions (about the number of players
   on a soccer team), the model briefly stated a general-knowledge fact
   before catching itself and adding the required refusal phrase. It's
   counted as a pass because the final answer correctly refused, but it
   shows the guardrail isn't perfectly airtight on every single response.
2. In a few answers, the model cited the wrong passage *number* in its
   own text (e.g. saying "passage 1" when it actually used passage 11).
   The retrieval step and the UI's "Retrieved: ..." display were correct
   every time — only the model's self-reported citation number was
   occasionally off. This doesn't affect what the user sees is actually
   being used, since the real source is always shown separately in the UI.

**Earlier finding (kept for reference):** the first version of the system
prompt was not strict enough — the model answered all out-of-scope
questions using outside knowledge (0/3 refused, tested on an earlier,
smaller test set). Rewriting the prompt to explicitly forbid outside
knowledge and require an exact refusal phrase fixed this.

---

## Problems encountered & how they were solved

| # | Problem | Solution |
|---|---|---|
| 1 | `foundry-local-sdk`'s API changed between versions (`foundry_local` module → `foundry_local_sdk`, CLI `service` command → `server`) | Rewrote scripts against the actually-installed SDK version (0.5.1 / CLI 1.2.4) instead of the tutorial's older API |
| 2 | C: drive had only ~15 GB free, causing the model's runtime scratch space to fail with `"Operation was cancelled"` | Freed disk space (Disk Cleanup, OneDrive Files On-Demand, Downloads cleanup) to ~22 GB free |
| 3 | Chat completion timed out on longer generations (default unlimited token output on a ~3-4 tokens/sec CPU) | Capped output with `max_tokens=100`, later raised to `max_tokens=180` once the timeout cause was understood |
| 4 | Model answered out-of-scope questions using outside knowledge instead of refusing (0/3 on an early guardrail test) | Rewrote the system prompt to explicitly forbid outside knowledge and require an exact refusal phrase |
| 5 | Streamlit couldn't find `rag.db` / `sample_docs.md` when launched from a different working directory | Resolved all file paths relative to the script's own location (`pathlib.Path(__file__).parent`) instead of the current working directory |
| 6 | Multiple duplicate README files accumulated from repeated downloads | Consolidated into a single `README.md` (this file) |
| 7 | Streamlit's default config exposed the app on the local network, not just this machine | Added `.streamlit/config.toml` with `address = "localhost"` to restrict access to this computer only |
| 8 | Model occasionally cites the wrong passage number in its answer text | Documented as a known limitation; UI shows the true retrieved source independently, so this doesn't mislead the user |

---

## Known limitations

- **Language:** the model (`phi-3.5-mini`, quantized for CPU) produces
  weak, repetitive output in Turkish. The knowledge base and expected
  questions are in English.
- **Speed:** CPU-only inference runs at roughly 3-4 tokens/second.
  Answers are capped at `max_tokens=180` to keep response times
  reasonable and avoid internal timeouts.
- **Instruction-following:** small local models need an explicit,
  strongly-worded system prompt to reliably refuse out-of-scope
  questions, and even then can occasionally leak a stray fact before
  self-correcting (see Test results above).
- **Citation accuracy:** the model's self-reported passage number in
  its answer text is sometimes wrong, even when the underlying
  retrieval was correct — the UI's separate source display is the
  reliable source of truth.
- **Scale:** retrieval works by loading all stored embeddings into
  memory and computing similarity in Python. This is fine for 15
  documents but would need a proper vector index for a much larger
  knowledge base.

---

## Lessons learned

- Foundry Local's SDK changed its API significantly between versions
  during this project — pinning dependency versions and reading the
  installed version's own docs mattered more than any tutorial.
- A weak/generic system prompt is not enough to stop a small model
  from answering outside its given context — the instruction needs
  to be explicit about the exact refusal wording expected.
- Splitting documents into small, well-defined passages made retrieval
  noticeably more accurate — even the weakest match among 15 passages
  still scored 0.52 and pointed to the right one.
- Showing the retrieval step in the UI (not just the final answer)
  builds trust: the user can see *why* an answer was given, and it
  makes the model's occasional wrong self-citation harmless rather
  than misleading.
- A local demo server is not automatically private — checking *which*
  address it binds to (localhost vs. network-wide) matters before
  sharing it with anyone.

---

## Possible next steps

- Expand the knowledge base further and test retrieval at larger scale.
- ~~Port `test_queries.py` to call the FastAPI `/api/query` endpoint instead
  of the legacy `rag.py` functions directly.~~ Done — re-run over HTTP,
  identical 15/15 + 5/5 result (see Test results above).
- Try a different small model to compare Turkish-language quality.
- Optional "enterprise" features seen in a peer project (`vectorvault-enterprise`,
  same internship cohort): streaming responses, per-source similarity
  scores, multi-format document upload, a FastAPI+React split, PDF
  report export, and a live system-telemetry page were all adopted
  (see below). JWT auth + audit logging and PII redaction were left
  out, since they require a multi-user deployment scenario this
  project doesn't have.

### Adopted from the peer project (Faz 4)

- **PDF export** (`POST /api/export/pdf`, "📄 Export PDF" button on
  each answer) — a branded one-page report with the query, topic,
  timestamp, the answer, and a References section listing each
  source's title and similarity score. Built with `reportlab`.
- **System telemetry page** (`GET /api/telemetry`, "📊 Telemetri" tab)
  — live CPU/RAM/disk usage bars (color-coded by severity), backend
  uptime, an "100% Offline" badge, and a knowledge-base breakdown by
  topic. Polls every 5 seconds. Built with `psutil`.
- **Input sanitization** (`backend/services/sanitize.py`) — every
  question passed to `/api/query` and `/api/query/stream` is first
  run through: Unicode normalization (NFKC), control-character
  stripping, whitespace collapsing, a 2000-character cap, and
  redaction of common prompt-injection phrases (e.g. "ignore all
  previous instructions", "reveal your system prompt", "you are now
  DAN...") to `[REDACTED]`. Tested with a mixed injection+legitimate
  question — the injected instruction was redacted and the assistant
  answered only the legitimate part, still refusing the out-of-scope
  part per the system prompt. This is a first line of defense, not a
  complete security solution.

---

## Legacy Streamlit version

Before the FastAPI + React rewrite, this project was a single-file
Streamlit app. It's kept in the repo (`app.py`, `rag.py`, `ingest.py`,
`embed_test.py`) as a record of the earlier, simpler iteration — it
still works standalone, independent of the `backend/`/`frontend/` folders:

```powershell
cd local-rag-assistant
venv\Scripts\activate
python ingest.py        # builds rag.db in the OLD single-table schema
streamlit run app.py
```

Note: the legacy `ingest.py` and the new `backend/seed.py` write
**different, incompatible schemas** to the same `rag.db` file (old:
one `documents` table with embeddings inline; new: `documents` +
`vector_chunks`). Running one after the other rebuilds the database
for that version — `backend/db.py` detects and migrates the old
schema automatically, but going back from new → old requires
re-running the legacy `ingest.py`. Don't run both apps against the
same `rag.db` at the same time.
