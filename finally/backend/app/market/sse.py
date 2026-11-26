"""Server-Sent Events formatting for price ticks (SPEC Section 6). No database access."""

import json
from collections.abc import Iterable, Iterator


def format_sse_event(event: str, data: dict) -> str:
    """Return one SSE frame: an event name line, a JSON data line, and a blank terminator."""
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


def format_price_events(ticks: Iterable[dict]) -> str:
    """Render each tick dict as a `price` SSE frame, concatenated in order."""
    return "".join(format_sse_event("price", dict(tick)) for tick in ticks)


def sse_event_generator(ticks: Iterable[dict]) -> Iterator[str]:
    """Yield one `price` SSE frame per tick dict, in order (SPEC Section 6 stream payload)."""
    for tick in ticks:
        yield format_sse_event("price", dict(tick))