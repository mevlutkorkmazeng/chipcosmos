# Semiconductor RAG Assistant

A fully offline Retrieval-Augmented Generation (RAG) Q&A assistant, built
on **Microsoft Foundry Local**. It answers questions about semiconductors
by retrieving relevant passages from a local knowledge base and grounding
the LLM's answer in that context — with no internet connection required
after setup.

Built as a one-month learning project following the plan in
"One-Month Project Plan: Local RAG AI Assistant with Microsoft Foundry Local".

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
 User question (browser, chat UI)
        │
        ▼
   Streamlit UI (app.py) ── keeps chat history in session state
        │
        ▼
   get_top_chunks() ── embeds query, compares against stored
        │               embeddings in rag.db (SQLite, 15 passages),
        │               returns (title, content, similarity score)
        ▼
   Top-2 relevant passages + scores
        │
        ▼
   answer_query() ── sends question + passages to phi-3.5-mini
        │              via Foundry Local, with a system prompt that
        │              restricts it to the given context and asks
        │              it to cite the passage used
        ▼
   Answer (grounded in context, cited, or an explicit refusal)
        │
        ▼
   Displayed in chat + "Retrieved: <passage> (score: X.XX)" shown below
```

Everything — the embedding model, the chat model, and the database — runs
**on this one machine**. Nothing is sent to the cloud, to Anthropic, or to
any external service. Foundry Local, Streamlit, and SQLite are all local
processes with no built-in connection to any AI assistant account.

---

## Security & access model

This project runs as a **local development server**, not a hosted website.

- **Where it runs:** entirely on this computer, as a local process
  (Streamlit's built-in dev server on port 8501). No cloud hosting, no
  external server, no deployment anywhere.
- **Who can reach it:** the app is configured to bind to `localhost`
  only (`.streamlit/config.toml`), so **only this computer** can open
  it — not even other devices on the same Wi-Fi network.
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

| File | Purpose |
|---|---|
| `hello_model.py` | Week 1 — verifies Foundry Local installation with a basic chat completion |
| `sample_docs.md` | The knowledge base — 15 passages covering semiconductor fundamentals through manufacturing and applications |
| `embed_test.py` | Week 2 — proves embedding + cosine similarity retrieval works |
| `ingest.py` | Week 2 — chunks `sample_docs.md`, embeds each passage, stores in `rag.db` |
| `rag.py` | Week 3-4 — core RAG logic: `get_top_chunks()` (with similarity scores) and `answer_query()` (with source citation) |
| `app.py` | Week 4 — Streamlit chat interface with history and retrieval transparency |
| `test_queries.py` | Week 5 — automated test suite (20 questions: 15 answerable, 5 out-of-scope) |

---

## Setup & running (Windows)

```powershell
cd local-rag-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# One-time: install the Foundry Local runtime if not already present
winget install Microsoft.FoundryLocal

# Build the knowledge base (only needs to be run once, or after editing sample_docs.md)
python ingest.py

# Launch the assistant (bound to localhost only, see Security section above)
streamlit run app.py
```

Then open the URL shown in the terminal (typically `http://localhost:8501`).

---

## Test results (Week 5)

An automated test suite (`test_queries.py`) ran 20 questions against the
assistant: one answerable question per knowledge-base passage (15 total),
and 5 deliberately out-of-scope questions spanning different topics
(geography, biology, math, sports, history).

| Metric | Result |
|---|---|
| Answerable questions correctly answered, with correct passage retrieved | 15 / 15 |
| Out-of-scope questions correctly refused | 5 / 5 |

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
- Add a confidence threshold: if the top similarity score is very low,
  have the assistant proactively say it's unsure rather than answering.
- Try a different small model to compare Turkish-language quality.
