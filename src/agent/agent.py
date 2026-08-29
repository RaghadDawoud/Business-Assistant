"""
Ties everything together: takes a user message, lets the LLM pick tool(s)
via function-calling, executes them, and returns a final natural-language
answer. Also reads/writes conversation memory.
"""
from src.agent.llm_client import chat
from src.agent.router import TOOLS, execute_tool_call
from src.memory import memory_store

SYSTEM_PROMPT = """You are a business assistant for a small Saudi retail/service business.
Answer in the same language the user writes in (Arabic or English).

For greetings and small talk (e.g. "hi", "thanks"), reply normally without calling any tool.

For factual questions about the business (policies, products, sales), first call the relevant
tool. Only answer using information the tools actually returned. If a tool returns nothing
relevant, or the question is outside what the tools cover, say clearly that you don't know /
don't have that information — do not guess or invent details such as company names, policies,
numbers, or products that weren't explicitly provided by a tool or by the user."""


def answer_query(user_id: str, user_message: str) -> str:
    history = memory_store.get_recent_history(user_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    # First call: let the model decide which tool(s) to use (if any)
    reply = chat(messages, tools=TOOLS)

    if reply.tool_calls:
        messages.append(reply)
        for tool_call in reply.tool_calls:
            result = execute_tool_call(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        # Second call: compose the final natural-language answer using tool results
        reply = chat(messages)

    final_answer = reply.content

    memory_store.log_message(user_id, "user", user_message)
    memory_store.log_message(user_id, "assistant", final_answer)

    return final_answer
