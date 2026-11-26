"""Message assembly and invocation for the FinAlly chat assistant LLM call."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from app.ai.prompts import SYSTEM_PROMPT, format_market_context
from app.ai.structured import parse_trade_intent


def build_messages(user_message: str, portfolio: dict, watchlist: list) -> list[dict]:
    """Build the chat message list: system prompt, market context, user turn."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": format_market_context(portfolio, watchlist)},
        {"role": "user", "content": user_message},
    ]


def _call_openrouter(messages: list[dict], api_key: str, model: str) -> str:
    """Call OpenRouter chat completions via litellm or urllib fallback."""
    # Try litellm if installed
    try:
        import litellm

        clean_model = model if model.startswith("openrouter/") else f"openrouter/{model}"
        response = litellm.completion(
            model=clean_model,
            messages=messages,
            api_key=api_key,
        )
        return response["choices"][0]["message"]["content"]
    except ImportError:
        pass

    # Direct HTTPS fallback to OpenRouter completions API (no external dependency)
    clean_model = model.removeprefix("openrouter/")
    req_body = json.dumps({
        "model": clean_model,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=req_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8010",
            "X-Title": "FinAlly Trading Workstation",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def generate_chat_response(messages: list, mock: bool) -> dict[str, Any]:
    """Return {"reply": str, "trade": dict | None} for a chat turn.

    mock=True yields deterministic output derived from the user turn.
    mock=False routes the messages to OpenRouter (gpt-4o-mini).
    """
    user_text = next(
        (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"),
        "",
    )
    trade = parse_trade_intent(user_text)

    if mock:
        if trade is not None:
            reply = f"Executed {trade['side']} {trade['quantity']:g} {trade['ticker']}."
        else:
            reply = f"You said: {user_text}"
        return {"reply": reply, "trade": trade}

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key or api_key == "your-openrouter-api-key-here":
        return {
            "reply": "No OPENROUTER_API_KEY found. Please set your key with 'export OPENROUTER_API_KEY=sk-...' before starting the app.",
            "trade": trade,
        }

    model = os.environ.get("LITELLM_MODEL", os.environ.get("OPENROUTER_MODEL", "openrouter/openai/gpt-4o-mini"))

    try:
        content = _call_openrouter(messages, api_key, model)
    except Exception as exc:
        return {
            "reply": f"OpenRouter API Error: {exc}",
            "trade": trade,
        }

    if not isinstance(content, str) or not content.strip():
        return {"reply": "The assistant returned an empty response.", "trade": trade}

    return {"reply": content.strip(), "trade": trade}
