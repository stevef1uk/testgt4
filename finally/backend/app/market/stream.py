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
    """Serialise a PriceTick into a JSON-safe dict."""
    return {
        "ticker": tick.ticker,
        "price": tick.price,
        "timestamp": tick.timestamp.isoformat(),
    }


def format_sse(event: str, data: Any) -> str:
    """Encode one SSE frame. `data` is JSON-encoded onto a single data line."""
    payload = json.dumps(data, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"


def format_comment(text: str = "keep-alive") -> str:
    """Encode an SSE comment frame (ignored by EventSource, keeps connection alive)."""
    return f": {text}\n\n"


async def price_events(
    cache: PriceCache,
    interval: float = DEFAULT_INTERVAL,
    max_events: int | None = None,
) -> AsyncIterator[str]:
    """Yield SSE frames containing the full latest-price snapshot every `interval` seconds.

    `max_events` bounds the generator (used by tests); None streams indefinitely.
    """
    sent = 0
    idle = 0
    while max_events is None or sent < max_events:
        ticks = await cache.get_all()
        if ticks:
            yield format_sse("prices", [tick_to_dict(t) for t in ticks])
            idle = 0
        else:
            idle += 1
            if idle % HEARTBEAT_EVERY == 0:
                yield format_comment()
        sent += 1
        await asyncio.sleep(interval)