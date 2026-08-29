"""
Ties everything together: takes a user message, lets the LLM pick tool(s)
via function-calling (possibly across several rounds for multi-part
questions), executes them, and returns a final natural-language answer.
Also reads/writes conversation memory.
"""
from src.agent.llm_client import chat
from src.agent.router import TOOLS, execute_tool_call
from src.memory import memory_store
from groq import BadRequestError

_capabilities_list = "\n".join(
    f"- {t['function']['name']}: {t['function']['description']}" for t in TOOLS
)

SYSTEM_PROMPT = f"""You are a business assistant for a small Saudi retail/service business.
Critical: always respond in the exact same language the user wrote in — never switch languages
mid-conversation.

Rules:
1. Greetings/small talk: reply normally, no tool call needed.
2. Factual questions: call the relevant tool first. Only answer using what the tool returned.
   If nothing relevant comes back, say you don't know — never invent facts, numbers, or names.
3. Sales/analysis questions require a period (month like "2025-01" or year like "2025").
   If missing, ask the user to clarify — never guess or default a period.
4. Multi-part questions: call every tool needed for every part before writing your final
   answer. If a question asks about several different things (e.g. top product by revenue
   AND best month), call a separate tool for each part — do not stop after the first result.
5. Unsupported analysis (e.g. profit margins, forecasting, YoY comparison): say you can't do
   it, then list what you can help with, from this capability list:
{_capabilities_list}"""

# Keywords that signal a data/sales question — used only as a safety net to
# force at least one tool call if the model tries to skip straight to an answer.
_DATA_KEYWORDS = [
    "sale", "sales", "revenue", "product", "month", "profit", "order",
    "مبيعات", "إيرادات", "منتج", "شهر", "أرباح", "طلب",
]


def _looks_like_data_question(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in _DATA_KEYWORDS)


MAX_TOOL_ROUNDS = 5  # safety cap so a confused model can't loop forever


def answer_query(user_id: str, user_message: str) -> str:
    history = memory_store.get_recent_history(user_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    force_first_call = _looks_like_data_question(user_message)

    reply = None
    for round_num in range(MAX_TOOL_ROUNDS):
        force_tools = force_first_call and round_num == 0
        try:
            reply = chat(messages, tools=TOOLS, force_tools=force_tools)
        except BadRequestError:
            # Model refused to call a tool even when required — accept its
            # text answer instead of crashing.
            reply = chat(messages, tools=TOOLS, force_tools=False)

        if not reply.tool_calls:
            break    

        print(f"[DEBUG] Round {round_num}: tools called: "
              f"{[tc.function.name for tc in reply.tool_calls]}")

        messages.append(reply)  # the assistant's tool-call message
        for tool_call in reply.tool_calls:
            result = execute_tool_call(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        # loop again: give the model a chance to call more tools or finish

    final_answer = reply.content if reply else "Sorry, something went wrong."

    memory_store.log_message(user_id, "user", user_message)
    memory_store.log_message(user_id, "assistant", final_answer)

    return final_answer