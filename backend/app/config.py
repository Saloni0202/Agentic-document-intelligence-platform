import os
from dotenv import load_dotenv

load_dotenv()

# Optional: set this to enable real LLM-generated answers.
# Without it, the agent still works — it just returns the retrieved
# context and tool results directly instead of an LLM-written synthesis.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "agent_docs")

# Chunking settings for ingested documents
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
