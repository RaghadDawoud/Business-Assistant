"""
Thin wrapper around the Groq API so the rest of the app never
touches the raw client directly (easier to swap models/providers later).
"""
from groq import Groq
import config

_client = Groq(api_key=config.GROQ_API_KEY)


def chat(messages: list[dict], tools: list[dict] | None = None, force_tools: bool = False):
    """Send a chat completion request to Groq. Returns the response message object."""
    kwargs = {"model": config.GROQ_MODEL, "messages": messages}

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "required" if force_tools else "auto"

    response = _client.chat.completions.create(**kwargs)
    return response.choices[0].message