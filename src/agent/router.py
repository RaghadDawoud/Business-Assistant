"""
Defines the tools (functions) the LLM is allowed to call, and turns a
tool_call from Groq into an actual Python function call.

This is the 'agent' brain: instead of regex/keyword matching, the LLM
decides which source(s) to use via native function-calling.
"""
import json

from src.rag.retriever import search_documents
from src.analysis import sales_functions as sf

# --- Tool schemas exposed to the LLM ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search company documents (policies, FAQs, product info) for an answer.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "monthly_revenue",
            "description": "Get total revenue for a given month (format YYYY-MM).",
            "parameters": {
                "type": "object",
                "properties": {"month": {"type": "string"}},
                "required": ["month"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_products",
            "description": "Get best-selling products, optionally for one month.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer"},
                    "month": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "low_performers",
            "description": "Get worst-selling products, optionally for one month.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer"},
                    "month": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sales_summary",
            "description": "Get a quick summary (revenue, orders, top product) for a month.",
            "parameters": {
                "type": "object",
                "properties": {"period": {"type": "string"}},
                "required": ["period"],
            },
        },
    },
]

# Maps tool name -> actual Python function to run
_FUNCTION_MAP = {
    "search_documents": search_documents,
    "monthly_revenue": sf.monthly_revenue,
    "top_products": sf.top_products,
    "low_performers": sf.low_performers,
    "sales_summary": sf.sales_summary,
}


def execute_tool_call(tool_call) -> str:
    """Run the function the LLM chose and return its result as a string."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments or "{}")
    func = _FUNCTION_MAP.get(name)
    if func is None:
        return f"Unknown tool: {name}"
    result = func(**args)
    return str(result)
