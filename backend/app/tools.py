"""
Tools the agent can call. Each tool is a plain Python function with a
JSON-schema-style description so it can also be handed to an LLM for
real function-calling (see agent.py) if an API key is configured.
"""
import ast
import operator as op
from typing import Dict

from app.vectorstore import vector_store

# ---- Tool: calculator -------------------------------------------------

_ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator_tool(expression: str) -> Dict:
    """Safely evaluate a basic arithmetic expression (+ - * / ** % //)."""
    try:
        tree = ast.parse(expression, mode="eval").body
        result = _safe_eval(tree)
        return {"tool": "calculator", "input": expression, "result": result}
    except Exception as e:
        return {"tool": "calculator", "input": expression, "error": str(e)}


# ---- Tool: document search (RAG retrieval) -----------------------------

def search_docs_tool(query: str, k: int = 4) -> Dict:
    """Retrieve the most relevant chunks from the ingested document store."""
    hits = vector_store.query(query, n_results=k)
    return {"tool": "search_docs", "input": query, "results": hits}


# ---- Tool registry (for the LLM function-calling path) ------------------

TOOL_SCHEMAS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '12*4+7'.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "search_docs",
        "description": "Search the ingested document collection for relevant passages.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

TOOL_IMPL = {
    "calculator": lambda args: calculator_tool(args["expression"]),
    "search_docs": lambda args: search_docs_tool(args["query"]),
}
