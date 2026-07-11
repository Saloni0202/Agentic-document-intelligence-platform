import { useState, useRef, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function ToolBadge({ tool }) {
  return <span className="tool-badge">{tool}</span>;
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! Upload a .txt/.md doc, then ask me about it — or throw me some math.", toolCalls: [] },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`).then((r) => r.json()).then(setHealth).catch(() => setHealth({ status: "unreachable" }));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", text: data.answer, toolCalls: data.tool_calls || [], mode: data.mode },
      ]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `Error contacting backend: ${e.message}`, toolCalls: [] }]);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const res = await fetch(`${API_BASE}/ingest`, { method: "POST", body: form });
      const data = await res.json();
      if (data.chunks_stored !== undefined) {
        setUploadStatus(`✓ ${file.name} ingested (${data.chunks_stored} chunks)`);
      } else {
        setUploadStatus(`Error: ${data.detail || "upload failed"}`);
      }
    } catch (err) {
      setUploadStatus(`Error: ${err.message}`);
    }
    e.target.value = "";
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Agentic RAG Assistant</h1>
          <p className="subtitle">Tool-calling agent · Vector retrieval · FastAPI + React</p>
        </div>
        <div className="status">
          <span className={`dot ${health?.status === "ok" ? "ok" : "bad"}`} />
          {health?.status === "ok"
            ? `Backend OK · ${health.llm_mode ? "LLM mode" : "Heuristic mode"} · ${health.docs_ingested.total_chunks} chunks`
            : "Backend unreachable"}
        </div>
      </header>

      <div className="upload-row">
        <label className="upload-btn">
          Upload document (.txt/.md)
          <input type="file" accept=".txt,.md" onChange={handleFileUpload} hidden />
        </label>
        {uploadStatus && <span className="upload-status">{uploadStatus}</span>}
      </div>

      <main className="chat">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <div className="bubble">
              <div className="bubble-text">{m.text}</div>
              {m.toolCalls && m.toolCalls.length > 0 && (
                <div className="tool-row">
                  {m.toolCalls.map((t, j) => (
                    <ToolBadge key={j} tool={t.tool} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="msg assistant"><div className="bubble typing">thinking…</div></div>}
        <div ref={bottomRef} />
      </main>

      <footer className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about your docs, or try 23*17+4"
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </footer>
    </div>
  );
}
