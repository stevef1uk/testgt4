"""Server-sent event formatting for market price updates."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping
from typing import Any


def encode_event(
    payload: Mapping[str, Any],
    *,
    event: str | None = None,
    event_id: str | None = None,
) -> str:
    """Encode one JSON payload using the SSE wire framing."""
    lines: list[str] = []
    if event_id is not None:
        lines.append(f"id: {event_id}")
    if event is not None:
        lines.append(f"event: {event}")
    lines.append(f"data: {json.dumps(dict(payload), separators=(',', ':'))}")
    return "\n".join(lines) + "\n\n"


def market_event(
    ticker: str,
    price: float,
    previous_price: float | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build the canonical frontend-facing market event payload."""
    if not ticker:
        raise ValueError("ticker must not be empty")
    if price < 0:
        raise ValueError("price must be non-negative")

    if previous_price is None or price == previous_price:
        direction = "unchanged"
    elif price > previous_price:
        direction = "up"
    else:
        direction = "down"

    return {
        "ticker": ticker,
        "price": float(price),
        "previous_price": previous_price,
        "timestamp": timestamp,
        "change_direction": direction,
    }


def stream_events(
    events: Iterable[Mapping[str, Any]],
    *,
    event: str | None = None,
) -> Iterator[str]:
    """Yield a finite or live iterable as SSE records."""
    for payload in events:
        yield encode_event(payload, event=event)