from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.vectorstore import vector_store
from app.agent import run_agent
from app.config import ANTHROPIC_API_KEY

app = FastAPI(title="Agentic RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_mode": bool(ANTHROPIC_API_KEY),
        "docs_ingested": vector_store.stats(),
    }


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """Upload a .txt or .md file to add it to the retrieval knowledge base."""
    if not file.filename.lower().endswith((".txt", ".md")):
        raise HTTPException(400, "Only .txt or .md files are supported in this MVP.")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8 encoded text.")
    n_chunks = vector_store.ingest(file.filename, text)
    return {"filename": file.filename, "chunks_stored": n_chunks}


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "message must not be empty")
    result = run_agent(req.message)
    return result


@app.get("/stats")
def stats():
    return vector_store.stats()
