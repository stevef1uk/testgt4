"""Parse and validate the LLM reply into the structured chat response schema."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)
_VALID_SIDES = ("buy", "sell")
_VALID_ACTIONS = ("add", "remove")


class ParseError(ValueError):
    """Raised when the LLM reply does not match the expected schema."""


@dataclass(frozen=True)
class TradeRequest:
    ticker: str
    side: str
    quantity: float


@dataclass(frozen=True)
class WatchlistChange:
    ticker: str
    action: str


@dataclass(frozen=True)
class ChatReply:
    message: str
    trades: list[TradeRequest] = field(default_factory=list)
    watchlist_changes: list[WatchlistChange] = field(default_factory=list)


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    match = _FENCE_RE.match(text)
    return match.group(1) if match else text


def _require_str(obj: dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ParseError(f"'{key}' must be a non-empty string")
    return value.strip()


def _parse_trade(item: Any) -> TradeRequest:
    if not isinstance(item, dict):
        raise ParseError("each trade must be an object")
    ticker = _require_str(item, "ticker").upper()
    side = _require_str(item, "side").lower()
    if side not in _VALID_SIDES:
        raise ParseError(f"trade side must be one of {_VALID_SIDES}")
    quantity = item.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, (int, float)):
        raise ParseError("trade quantity must be a number")
    if quantity <= 0:
        raise ParseError("trade quantity must be positive")
    return TradeRequest(ticker=ticker, side=side, quantity=float(quantity))


def _parse_watchlist_change(item: Any) -> WatchlistChange:
    if not isinstance(item, dict):
        raise ParseError("each watchlist change must be an object")
    ticker = _require_str(item, "ticker").upper()
    action = _require_str(item, "action").lower()
    if action not in _VALID_ACTIONS:
        raise ParseError(f"watchlist action must be one of {_VALID_ACTIONS}")
    return WatchlistChange(ticker=ticker, action=action)


def parse_chat_reply(raw: str) -> ChatReply:
    """Parse the raw model text into a validated ``ChatReply``.

    Accepts the bare JSON object or one wrapped in a markdown code fence.
    Missing optional lists default to empty. Raises ``ParseError`` on any
    schema violation so the caller can fall back to a safe error response.
    """
    try:
        data = json.loads(_strip_fences(raw))
    except json.JSONDecodeError as exc:
        raise ParseError(f"reply is not valid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ParseError("reply must be a JSON object")

    message = _require_str(data, "message")

    raw_trades = data.get("trades", [])
    if not isinstance(raw_trades, list):
        raise ParseError("'trades' must be a list")
    raw_changes = data.get("watchlist_changes", [])
    if not isinstance(raw_changes, list):
        raise ParseError("'watchlist_changes' must be a list")

    return ChatReply(
        message=message,
        trades=[_parse_trade(t) for t in raw_trades],
        watchlist_changes=[_parse_watchlist_change(c) for c in raw_changes],
    )