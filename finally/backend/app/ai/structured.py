"""Structured trade-intent parsing for chat messages."""

from __future__ import annotations

import re

_TRADE_RE = re.compile(
    r"^\s*(buy|sell)\s+(\d+(?:\.\d+)?)\s+([A-Za-z]{1,10})\s*$",
    re.IGNORECASE,
)


def parse_trade_intent(user_message: str) -> dict | None:
    """Return {"ticker", "side", "quantity"} for a simple trade command, else None."""
    match = _TRADE_RE.match(user_message or "")
    if match is None:
        return None
    side, qty_text, ticker = match.groups()
    quantity = float(qty_text)
    if quantity <= 0:
        return None
    return {"ticker": ticker.upper(), "side": side.lower(), "quantity": quantity}