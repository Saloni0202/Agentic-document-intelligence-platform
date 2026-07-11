# 🤖 Agentic Document Intelligence Platform

### AI-Powered Retrieval-Augmented Generation (RAG) Assistant with Tool Calling

An intelligent document assistant that enables users to upload their own documents and interact with them through natural language conversations. The platform combines Retrieval-Augmented Generation (RAG), semantic search, and agentic tool invocation to provide accurate, context-aware responses over private documents.

Unlike traditional chatbots, the system can intelligently decide whether to retrieve information from documents or invoke external tools to answer a user's query.

---

# 📌 Overview

The platform is designed around the principles of **Agentic Engineering**, where an AI agent can:

* Understand user intent
* Retrieve information from uploaded documents
* Invoke tools when necessary
* Generate context-aware responses
* Operate in both offline and LLM-assisted modes

The application supports conversational question answering over private knowledge bases while remaining lightweight and easy to deploy.

---

# ✨ Features

* 📄 Document upload and ingestion (`.txt` and `.md`)
* 🔍 Semantic document search
* 🤖 Retrieval-Augmented Generation (RAG)
* 🧠 Agentic tool invocation
* 🧮 Secure calculator tool
* 💬 Conversational chat interface
* 💾 Persistent local vector database
* 🌐 Offline-first architecture
* 🔑 Optional Anthropic Claude integration
* 🏗 Modular and extensible architecture

---

# 🏗 System Architecture

```text
┌─────────────┐        HTTP (fetch)        ┌──────────────────┐
│   React UI   │ ───────────────────────▶  │   FastAPI backend │
│ (Vite, chat  │ ◀───────────────────────  │                    │
│  + upload)   │        JSON response       │  /ingest /chat     │
└─────────────┘                            └─────────┬──────────┘
                                                       │
                                     ┌─────────────────┼─────────────────┐
                                     ▼                                   ▼
                            ┌─────────────────┐              ┌────────────────────┐
                            │   Agent Router   │────────────▶│      Tools          │
                            │ (Heuristic/LLM)  │             │ Calculator Tool     │
                            └─────────────────┘              │ Document Search     │
                                                              └─────────┬──────────┘
                                                                        │
                                                                        ▼
                                                          ┌────────────────────┐
                                                          │ ChromaDB Vector DB │
                                                          │ Persistent Storage │
                                                          └────────────────────┘
```

---

# 🔄 Workflow

## Document Ingestion

```text
User Uploads Document
          ↓
Document Chunking
          ↓
Embedding Generation
          ↓
ChromaDB Storage
```

## Query Processing

```text
User Query
      ↓
Agent Router
      ↓
Tool Selection
      ↓
Context Retrieval
      ↓
Response Generation
      ↓
Chat Interface
```

---

# 🧠 Agent Modes

### Offline Mode

* No API key required.
* Uses a lightweight heuristic router.
* Arithmetic queries invoke the calculator tool.
* Information queries invoke the document search tool.

### LLM Mode

* Enabled through `ANTHROPIC_API_KEY`.
* Uses real tool-calling capabilities.
* The LLM decides which tools to invoke and synthesizes the final response.

---

# 💡 Design Decisions

### Offline-first Embeddings

The platform uses deterministic hashing-based embeddings instead of downloading large embedding models, enabling:

* Low-cost deployments
* Faster setup
* Operation on restricted networks

The embedding implementation can easily be replaced with:

* sentence-transformers/all-MiniLM-L6-v2
* OpenAI Embeddings
* Gemini Embeddings

---

### Secure Tool Invocation

Arithmetic expressions are evaluated through a restricted AST parser instead of Python's `eval()`, preventing arbitrary code execution.

---

# 🛠 Tech Stack

| Component       | Technology                     |
| --------------- | ------------------------------ |
| Backend         | FastAPI                        |
| Frontend        | React + Vite                   |
| Vector Database | ChromaDB                       |
| Language        | Python                         |
| AI              | Retrieval-Augmented Generation |
| LLM             | Anthropic Claude API           |
| Storage         | Persistent Local Storage       |

---

# 📂 Project Structure

```text
agentic-document-intelligence-platform/
│
├── frontend/
│   ├── src/
│   └── public/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agent.py
│   │   ├── tools.py
│   │   ├── vectorstore.py
│   │   └── config.py
│
├── requirements.txt
└── README.md
```

---

# 🚀 Applications

* Enterprise Knowledge Assistants
* Internal Documentation Search
* Research Assistants
* Educational Chatbots
* Customer Support Systems
* Personal Knowledge Management

---

# 🔮 Future Enhancements

* PDF and DOCX support
* Multi-agent architecture
* Authentication and user management
* Docker deployment
* CI/CD pipeline
* Citation generation
* Web search integration
* Session-based chat history

---

# 📚 Learning Outcomes

* Retrieval-Augmented Generation (RAG)
* Agentic AI Systems
* Vector Databases
* FastAPI Backend Development
* React Frontend Development
* Tool Calling Architectures
* Full-Stack AI Application Development

---

# 👩‍💻 Author

**Saloni**
B.Tech CSE (AI & ML)
VIT Bhopal University
