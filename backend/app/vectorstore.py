"""
Thin wrapper around ChromaDB for document ingestion + retrieval.

Uses Chroma's bundled default embedding function (ONNX MiniLM) so there is
no dependency on torch / sentence-transformers and no external API call
required just to embed text.
"""
import hashlib
import math
import uuid
from typing import List, Dict

import chromadb

from app.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP

VECTOR_DIM = 384


class HashingEmbeddingFunction:
    """
    Lightweight, fully offline embedding function using the hashing trick
    (signed feature hashing over lowercased tokens, L2-normalized).

    This avoids pulling a large model at runtime, which is fine for an
    MVP/demo and keeps the whole stack dependency-light. The interface
    matches Chroma's EmbeddingFunction protocol, so swapping in a real
    model later (e.g. sentence-transformers/all-MiniLM-L6-v2, or an
    API-based embedding model) is a one-line change in this file.
    """

    def name(self) -> str:
        return "hashing-embedding-v1"

    def __call__(self, input: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * VECTOR_DIM
        tokens = text.lower().split()
        for tok in tokens:
            digest = hashlib.md5(tok.encode("utf-8")).hexdigest()
            h = int(digest, 16)
            idx = h % VECTOR_DIM
            sign = 1.0 if (h // VECTOR_DIM) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Simple sliding-window chunker over raw text."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.embedding_fn = HashingEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
        )

    def ingest(self, source_name: str, text: str) -> int:
        """Chunk + embed + store a document. Returns number of chunks stored."""
        chunks = chunk_text(text)
        if not chunks:
            return 0
        ids = [f"{source_name}-{uuid.uuid4().hex[:8]}-{i}" for i in range(len(chunks))]
        metadatas = [{"source": source_name, "chunk_index": i} for i in range(len(chunks))]
        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        return len(chunks)

    def query(self, query_text: str, n_results: int = 4) -> List[Dict]:
        """Return top-k relevant chunks with metadata + distance score."""
        if self.collection.count() == 0:
            return []
        n_results = min(n_results, self.collection.count())
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        hits = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        for doc, meta, dist in zip(docs, metas, dists):
            hits.append({"text": doc, "source": meta.get("source"), "score": dist})
        return hits

    def stats(self) -> Dict:
        return {"total_chunks": self.collection.count()}


# Singleton instance used by the app
vector_store = VectorStore()
