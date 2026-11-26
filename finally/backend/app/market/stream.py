"""Server-Sent Events helpers for streaming live prices to the browser."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from app.market.base import PriceTick
from app.market.cache import PriceCache

DEFAULT_INTERVAL = 1.0  # seconds between pushes
HEARTBEAT_EVERY = 15  # emit a comment frame every N intervals to keep proxies open


def tick_to_dict(tick: PriceTick) -> dict[str, Any]:
    """Serialise a PriceTick into a JSON-safe dict matching SPEC Section 6."""
    return {
        "ticker": tick.ticker,
        "price": tick.price,
        "previous_price": tick.previous_price,
        "change": tick.change,
        "change_percent": tick.change_percent,
        "change_direction": tick.change_direction,
        "timestamp": tick.timestamp.isoformat(),
    }


def format_sse(event: str | None, data: Any) -> str:
    """Encode one SSE frame.

    If `event` is non-empty, emits `event: <event>\\ndata: <json>\\n\\n`.
    If `event` is None or empty, emits standard unnamed `data: <json>\\n\\n`.
    """
    payload = json.dumps(data, separators=(",", ":"))
    if event:
        return f"event: {event}\ndata: {payload}\n\n"
    return f"data: {payload}\n\n"


def format_comment(text: str = "keep-alive") -> str:
    """Encode an SSE comment frame (ignored by EventSource, keeps connection alive)."""
    return f": {text}\n\n"


async def price_events(
    cache: PriceCache,
    interval: float = DEFAULT_INTERVAL,
    max_events: int | None = None,
) -> AsyncIterator[str]:
    """Yield SSE frames containing live price updates per SPEC Section 6.

    SPEC requirements:
    - Each SSE event contains ticker, price, previous price, change, change percent, timestamp, change_direction.
    - Yields both named events (`event: price`) and standard data lines (`data: {...}`).
    """
    sent = 0
    idle = 0
    while max_events is None or sent < max_events:
        ticks = await cache.get_all()
        if ticks:
            # Yield named events for addEventListener("price")
            for t in ticks:
                yield format_sse("price", tick_to_dict(t))
            # Also yield unnamed data line with array of ticks for onmessage handlers
            yield format_sse(None, [tick_to_dict(t) for t in ticks])
            idle = 0
        else:
            idle += 1
            if idle % HEARTBEAT_EVERY == 0:
                yield format_comment()
        sent += 1
        await asyncio.sleep(interval)
