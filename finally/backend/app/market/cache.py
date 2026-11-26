"""In-memory cache of the latest price tick per ticker."""

from __future__ import annotations

import asyncio

from app.market.base import PriceTick


class PriceCache:
    """Stores the most recent PriceTick for each ticker.

    Writes come from the poller/simulator; reads come from the SSE stream
    and API routes. An asyncio.Lock guards concurrent access.
    """

    def __init__(self) -> None:
        self._ticks: dict[str, PriceTick] = {}
        self._lock = asyncio.Lock()

    async def update(self, tick: PriceTick) -> None:
        """Store the latest tick for its ticker, replacing any previous value."""
        async with self._lock:
            self._ticks[tick.ticker] = tick

    async def get(self, ticker: str) -> PriceTick | None:
        """Return the latest tick for a ticker, or None if unknown."""
        async with self._lock:
            return self._ticks.get(ticker)

    async def get_all(self) -> list[PriceTick]:
        """Return the latest tick for every cached ticker."""
        async with self._lock:
            return list(self._ticks.values())

    async def remove(self, ticker: str) -> None:
        """Drop a ticker from the cache. Missing tickers are ignored."""
        async with self._lock:
            self._ticks.pop(ticker, None)

    async def clear(self) -> None:
        """Remove all cached ticks."""
        async with self._lock:
            self._ticks.clear()

    def __len__(self) -> int:
        return len(self._ticks)