"""In-memory cache of the latest price tick and prior price per ticker."""

from __future__ import annotations

import asyncio

from app.market.base import PriceTick


def _calc_change(current: float, prev: float | None) -> tuple[float, float, str]:
    if prev is None or prev == 0:
        return 0.0, 0.0, "flat"
    diff = round(current - prev, 4)
    pct = round((diff / prev) * 100.0, 4)
    direction = "up" if diff > 0 else "down" if diff < 0 else "flat"
    return diff, pct, direction


class PriceCache:
    """Stores the latest and previous PriceTick for each ticker per SPEC Section 6.

    Writes come from the poller/simulator; reads come from the SSE stream
    and API routes. An asyncio.Lock guards concurrent access.
    """

    def __init__(self) -> None:
        self._ticks: dict[str, PriceTick] = {}
        self._previous_prices: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def update(self, tick: PriceTick) -> None:
        """Store the latest tick for its ticker, computing previous price, change, and direction."""
        async with self._lock:
            prev = self._previous_prices.get(tick.ticker)
            if prev is None and tick.ticker in self._ticks:
                prev = self._ticks[tick.ticker].price

            diff, pct, direction = _calc_change(tick.price, prev)
            updated_tick = PriceTick(
                ticker=tick.ticker,
                price=tick.price,
                previous_price=prev,
                change=diff,
                change_percent=pct,
                change_direction=direction,
                timestamp=tick.timestamp,
            )
            self._previous_prices[tick.ticker] = tick.price
            self._ticks[tick.ticker] = updated_tick

    async def get(self, ticker: str) -> PriceTick | None:
        """Return the latest tick for a ticker, or None if unknown."""
        async with self._lock:
            return self._ticks.get(ticker)

    async def get_previous_price(self, ticker: str) -> float | None:
        """Return the previous price observed before the current tick."""
        async with self._lock:
            return self._previous_prices.get(ticker)

    async def get_all(self) -> list[PriceTick]:
        """Return the latest tick for every cached ticker."""
        async with self._lock:
            return list(self._ticks.values())

    async def remove(self, ticker: str) -> None:
        """Drop a ticker from the cache. Missing tickers are ignored."""
        async with self._lock:
            self._ticks.pop(ticker, None)
            self._previous_prices.pop(ticker, None)

    async def clear(self) -> None:
        """Remove all cached ticks."""
        async with self._lock:
            self._ticks.clear()
            self._previous_prices.clear()

    def __len__(self) -> int:
        return len(self._ticks)
