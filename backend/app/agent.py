"""
Agent orchestration layer.

Two modes:
1. LLM mode (ANTHROPIC_API_KEY set): sends the user message + tool schemas
   to Claude, lets Claude decide which tool(s) to call via real function
   calling, executes them, and feeds results back for a final answer.
2. Heuristic mode (no API key): a lightweight rule-based router so the
   whole pipeline is runnable and demoable with zero external cost/keys.
   This is what most people will run first before wiring up a key.
"""
import re
from typing import Dict, List

from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from app.tools import TOOL_SCHEMAS, TOOL_IMPL, calculator_tool, search_docs_tool

_MATH_PATTERN = re.compile(r"^[\d\s\+\-\*/\(\)\.\%]+$")


def _looks_like_math(text: str) -> bool:
    stripped = text.strip().rstrip("?")
    return bool(_MATH_PATTERN.match(stripped)) and any(c.isdigit() for c in stripped)


def run_heuristic_agent(message: str) -> Dict:
    """No-LLM fallback: simple keyword/pattern routing between tools."""
    if _looks_like_math(message):
        result = calculator_tool(message.strip().rstrip("?"))
        if "error" not in result:
            answer = f"Result: {result['result']}"
        else:
            answer = f"Couldn't evaluate that expression: {result['error']}"
        return {"answer": answer, "tool_calls": [result], "mode": "heuristic"}

    # default: treat as a retrieval question over ingested docs
    result = search_docs_tool(message)
    hits = result["results"]
    if not hits:
        answer = ("No documents have been ingested yet (or nothing relevant was found). "
                   "Upload a document via /ingest, then ask again.")
    else:
        preview = "\n\n".join(f"[{h['source']}] {h['text'][:300]}" for h in hits[:3])
        answer = ("No LLM key configured, so here are the raw retrieved passages "
                   f"most relevant to your question:\n\n{preview}")
    return {"answer": answer, "tool_calls": [result], "mode": "heuristic"}


def run_llm_agent(message: str) -> Dict:
    """Real tool-calling loop using Claude's Messages API."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    messages: List[Dict] = [{"role": "user", "content": message}]
    tool_calls_made = []

    system = (
        "You are a helpful assistant with access to tools: a calculator and a "
        "document search tool over a user-provided knowledge base. Use search_docs "
        "for factual/document questions, calculator for arithmetic. Cite which "
        "source a fact came from when you use search_docs results."
    )

    for _ in range(4):  # cap tool-use loop iterations
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system=system,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            final_text = "".join(b.text for b in response.content if b.type == "text")
            return {"answer": final_text, "tool_calls": tool_calls_made, "mode": "llm"}

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                impl = TOOL_IMPL.get(block.name)
                result = impl(block.input) if impl else {"error": f"Unknown tool {block.name}"}
                tool_calls_made.append(result)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return {"answer": "Reached max tool-use iterations without a final answer.",
            "tool_calls": tool_calls_made, "mode": "llm"}


def run_agent(message: str) -> Dict:
    if ANTHROPIC_API_KEY:
        return run_llm_agent(message)
    return run_heuristic_agent(message)
