"""Simulated price source: geometric random walk per ticker."""

from __future__ import annotations

import asyncio
import math
import random
from datetime import datetime, timezone

from app.market.base import PriceSource, PriceTick

DEFAULT_START_PRICE = 100.0
DEFAULT_VOLATILITY = 0.02  # per-step standard deviation of log returns


class SimulatedPriceSource(PriceSource):
    """Generates plausible prices without network access.

    Each call to get_prices() advances every tracked ticker by one random
    step. Pass a seed for deterministic output (useful in tests).
    """

    def __init__(
        self,
        start_prices: dict[str, float] | None = None,
        volatility: float = DEFAULT_VOLATILITY,
        seed: int | None = None,
    ) -> None:
        if volatility < 0:
            raise ValueError("volatility must be non-negative")
        self._start_prices = dict(start_prices or {})
        self._volatility = volatility
        self._rng = random.Random(seed)
        self._prices: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def start(self, tickers: list[str]) -> None:
        async with self._lock:
            self._prices = {}
            for ticker in dict.fromkeys(tickers):
                self._seed_ticker(ticker)

    async def stop(self) -> None:
        async with self._lock:
            self._prices.clear()

    async def add_ticker(self, ticker: str) -> None:
        async with self._lock:
            if ticker not in self._prices:
                self._seed_ticker(ticker)

    async def remove_ticker(self, ticker: str) -> None:
        async with self._lock:
            self._prices.pop(ticker, None)

    async def get_prices(self) -> list[PriceTick]:
        async with self._lock:
            now = datetime.now(timezone.utc)
            ticks: list[PriceTick] = []
            for ticker in self._prices:
                self._step(ticker)
                ticks.append(
                    PriceTick(ticker=ticker, price=self._prices[ticker], timestamp=now)
                )
            return ticks

    def _seed_ticker(self, ticker: str) -> None:
        self._prices[ticker] = self._start_prices.get(ticker, DEFAULT_START_PRICE)

    def _step(self, ticker: str) -> None:
        shock = self._rng.gauss(0.0, self._volatility)
        self._prices[ticker] = round(self._prices[ticker] * math.exp(shock), 4)