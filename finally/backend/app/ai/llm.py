"""Message assembly for the FinAlly chat assistant LLM call."""

from __future__ import annotations

import os

from app.ai.prompts import SYSTEM_PROMPT, format_market_context
from app.ai.structured import parse_trade_intent


def build_messages(user_message: str, portfolio: dict, watchlist: list) -> list[dict]:
    """Build the chat message list: system prompt, market context, user turn."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": format_market_context(portfolio, watchlist)},
        {"role": "user", "content": user_message},
    ]


def generate_chat_response(messages: list, mock: bool) -> dict:
    """Return {"reply": str, "trade": dict | None} for a chat turn.

    mock=True yields deterministic output derived from the user turn.
    mock=False routes the messages through LiteLLM (OpenRouter model).
    Malformed or failed model output never raises to the caller.
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

    try:
        import litellm  # imported lazily so mock mode needs no network stack

        model = os.environ.get("LITELLM_MODEL", "openrouter/openai/gpt-4o-mini")
        response = litellm.completion(model=model, messages=messages)
        content = response["choices"][0]["message"]["content"]
    except Exception:
        return {"reply": "The assistant is unavailable right now.", "trade": None}

    if not isinstance(content, str) or not content.strip():
        return {"reply": "The assistant returned an empty response.", "trade": None}
    return {"reply": content.strip(), "trade": trade}