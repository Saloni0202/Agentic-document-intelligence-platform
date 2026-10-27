# 📄 Agentic Document Intelligence Platform

### AI-Powered Document Assistant using RAG & Tool Calling

An intelligent document assistant that allows users to upload documents and ask questions through natural language conversations. It combines semantic search, Retrieval-Augmented Generation (RAG), and agentic tool calling to retrieve relevant information and generate context-aware responses.

Unlike traditional chatbots, the platform can route queries to appropriate tools, including document search and a secure calculator, with support for both offline and LLM-powered execution.

## ✨ Key Features

- 📄 **Document Ingestion:** Upload and process `.txt` and `.md` files.
- 🔍 **Semantic Search:** Retrieve relevant information from stored documents.
- 🧠 **RAG Pipeline:** Generate responses using retrieved document context.
- 🤖 **Agentic Tool Calling:** Select appropriate tools based on user queries.
- 🧮 **Secure Calculator:** Evaluate arithmetic expressions without using Python's unrestricted `eval()`.
- 💬 **Interactive Chat Interface:** Query documents through a React-based interface.
- 💾 **Persistent Vector Storage:** Store document representations using ChromaDB.
- 🌐 **Dual Execution Modes:** Support lightweight offline routing and Claude-powered tool calling.

## 🏗️ Architecture

The application follows a modular full-stack architecture:

- **Frontend:** React and Vite provide the chat interface and document upload functionality.
- **Backend:** FastAPI handles document ingestion, query processing, and API communication.
- **Agent Router:** Determines which tool should handle each query.
- **Tool Layer:** Executes document retrieval or calculator operations.
- **Vector Database:** ChromaDB stores document embeddings for retrieval.

## 🔄 Workflow

1. **Document Ingestion:** Uploaded files are divided into smaller chunks.
2. **Embedding Generation:** Text chunks are converted into vector representations.
3. **Vector Storage:** Embeddings are stored persistently in ChromaDB.
4. **Query Routing:** The agent identifies the appropriate tool for the user's query.
5. **Context Retrieval:** Relevant document chunks are retrieved when required.
6. **Response Generation:** The system returns an answer using the available context and, in LLM mode, Claude's response-generation capabilities.

## 🧠 Agent Execution Modes

- **Offline Mode:** Uses heuristic-based routing and local tools without requiring an LLM API key.
- **LLM Mode:** Integrates the Anthropic Claude API for model-driven tool selection and response generation.

The embedding implementation uses deterministic hashing-based representations to support lightweight setup without downloading a large embedding model.

## 🛠️ Tech Stack

`Python` · `FastAPI` · `React` · `Vite` · `ChromaDB` · `RAG` · `Anthropic Claude API` · `REST APIs`

## 🎯 Applications

- Enterprise knowledge management
- Internal documentation search
- Research and study assistants
- Educational question-answering systems
- Document-based customer support

## 🔮 Future Enhancements

- PDF and DOCX document support
- Source citations for generated answers
- User authentication and session management
- Web search integration
- Docker-based deployment

---

**Author:** Saloni Maijorwar| B.Tech CSE (AI & ML), VIT Bhopal University
