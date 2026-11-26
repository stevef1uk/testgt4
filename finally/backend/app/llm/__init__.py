"""LLM package: client, prompts, reply parsing, and chat orchestration."""

from app.llm.chat_service import FALLBACK_MESSAGE, ChatService
from app.llm.client import (
    LLMClient,
    LLMError,
    MockLLMClient,
    OpenAICompatibleClient,
    create_llm_client,
)
from app.llm.parser import (
    ChatReply,
    ParseError,
    TradeRequest,
    WatchlistChange,
    parse_chat_reply,
)
from app.llm.prompts import SYSTEM_PROMPT, build_market_context, build_system_messages

__all__ = [
    "FALLBACK_MESSAGE",
    "SYSTEM_PROMPT",
    "ChatReply",
    "ChatService",
    "LLMClient",
    "LLMError",
    "MockLLMClient",
    "OpenAICompatibleClient",
    "ParseError",
    "TradeRequest",
    "WatchlistChange",
    "build_market_context",
    "build_system_messages",
    "create_llm_client",
    "parse_chat_reply",
]