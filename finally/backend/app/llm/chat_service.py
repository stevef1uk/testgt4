"""Chat orchestration: build context, call the LLM, and parse the structured reply."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.llm.client import LLMClient, LLMError
from app.llm.parser import ChatReply, ParseError, parse_chat_reply
from app.llm.prompts import SYSTEM_PROMPT, build_market_context

FALLBACK_MESSAGE = (
    "Sorry, I couldn't process that response. Please try rephrasing your request."
)


class ChatService:
    """Answers a user message using the LLM with live portfolio context."""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def respond(
        self,
        user_message: str,
        cash: float,
        positions: Sequence[Mapping[str, Any]],
        watchlist: Sequence[str],
        prices: Mapping[str, float],
    ) -> ChatReply:
        """Return a validated ``ChatReply`` for the user's message.

        Provider failures and malformed model output both degrade to a
        fallback reply with no trades, so the caller never executes an
        unparsed action.
        """
        context = build_market_context(cash, positions, watchlist, prices)
        user_content = f"Current market context:\n{context}\n\nUser message: {user_message}"
        try:
            raw = self._client.complete(SYSTEM_PROMPT, user_content)
        except LLMError:
            return ChatReply(message=FALLBACK_MESSAGE)
        try:
            return parse_chat_reply(raw)
        except ParseError:
            return ChatReply(message=FALLBACK_MESSAGE)