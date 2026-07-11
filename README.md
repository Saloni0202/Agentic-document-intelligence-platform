# Agentic RAG Assistant

A small agent that answers questions over your own documents (RAG) and can
call tools (calculator, document search) instead of just chatting. Built as
an MVP for the "Agentic Engineering" focus area — meant to be extended, not
a finished product.

## Architecture

```
┌─────────────┐        HTTP (fetch)        ┌──────────────────┐
│   React UI   │ ───────────────────────▶  │   FastAPI backend │
│ (Vite, chat  │ ◀───────────────────────  │                    │
│  + upload)   │        JSON response       │  /ingest /chat     │
└─────────────┘                            └─────────┬──────────┘
                                                       │
                                     ┌─────────────────┼─────────────────┐
                                     ▼                                   ▼
                            ┌─────────────────┐              ┌────────────────────┐
                            │   Agent router   │              │     Tools           │
                            │ (agent.py)        │─────calls──▶│ calculator_tool      │
                            │ heuristic OR       │              │ search_docs_tool     │
                            │ Claude tool-use     │              └─────────┬────────────┘
                            └────────────────────┘                        │
                                                                            ▼
                                                                ┌────────────────────┐
                                                                │  ChromaDB (local)    │
                                                                │  offline hashing      │
                                                                │  embeddings           │
                                                                └────────────────────┘
```

**Request flow:**
1. User uploads a `.txt`/`.md` file → backend chunks it → embeds each chunk
   (offline hashing-trick embedding, no external model download) → stores
   in a local persistent ChromaDB collection.
2. User sends a chat message → the agent decides which tool to use:
   - **No `ANTHROPIC_API_KEY` set:** a lightweight heuristic router (regex
     for arithmetic → calculator; otherwise → document search) — runs
     fully offline, zero cost, good for demos.
   - **`ANTHROPIC_API_KEY` set:** real LLM tool-calling — Claude decides
     which tool(s) to invoke, the backend executes them, results are fed
     back for a final synthesized answer.
3. Response (answer + which tools were called) is returned to the UI,
   which shows tool badges next to each agent reply.

## Why it's built this way (design notes for interviews)

- **Offline-first embeddings:** instead of depending on downloading a
  ~90MB embedding model at first run (fragile on restricted networks),
  chunk embeddings use a deterministic hashing-trick vectorizer. This is
  a known-weaker retrieval quality trade-off, documented here on purpose —
  the natural next step is swapping in `sentence-transformers/all-MiniLM-L6-v2`
  or an API embedding model, which is a one-line change in `vectorstore.py`
  because the interface matches Chroma's `EmbeddingFunction` protocol.
- **Two agent modes, not one:** the heuristic router means the whole app
  is demoable and testable with zero API keys/cost. The LLM mode is real
  Anthropic function-calling, not a mock — swap in a key and it upgrades
  automatically.
- **Guardrailed calculator tool:** arithmetic is evaluated via a restricted
  AST walker (`tools.py`), not Python `eval()`, so it can't execute
  arbitrary code.

## Project status

🚧 **In progress.** Current state: ingestion, retrieval, calculator tool,
heuristic + LLM agent modes, and chat UI all work end-to-end locally.

Roadmap:
- [ ] Swap hashing embeddings for a real embedding model
- [ ] Add a third tool (e.g. web search or a public API call)
- [ ] Persist chat history per session
- [ ] Add PDF ingestion support
- [ ] Dockerize + CI pipeline

## Running it

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # optional: add ANTHROPIC_API_KEY to enable LLM mode
uvicorn app.main:app --reload --port 8000
```
Backend runs at `http://127.0.0.1:8000`. Check `http://127.0.0.1:8000/health`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://127.0.0.1:5173` and talks to the backend at
`http://127.0.0.1:8000` by default (override with a `VITE_API_BASE` env var
in a `.env` file in `frontend/` if needed).

### Try it
1. Open the frontend in your browser.
2. Upload a `.txt` or `.md` file using the upload button.
3. Ask a question about its content — the agent will call the search tool.
4. Ask a math question like `23*17+4` — the agent will call the calculator tool.
5. (Optional) Add your `ANTHROPIC_API_KEY` in `backend/.env` and restart the
   backend to switch from heuristic routing to real LLM tool-calling.

## Tech stack
FastAPI · ChromaDB · React (Vite) · Anthropic Claude API (optional, for LLM tool-calling)
