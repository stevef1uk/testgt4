"""Live market data source backed by the Massive REST API."""

from __future__ import annotations

import asyncio
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from app.market.base import PriceSource, PriceTick

DEFAULT_BASE_URL = "https://api.massive.com"


class MassiveClient(PriceSource):
    """Fetches last-trade prices for tracked tickers via the snapshot endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required for MassiveClient")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._tickers: list[str] = []
        self._latest: dict[str, PriceTick] = {}
        self._lock = asyncio.Lock()

    async def start(self, tickers: list[str]) -> None:
        async with self._lock:
            self._tickers = list(dict.fromkeys(tickers))

    async def stop(self) -> None:
        async with self._lock:
            self._tickers = []
            self._latest.clear()

    async def get_price(self, ticker: str) -> float | None:
        async with self._lock:
            tick = self._latest.get(ticker)
            return tick.price if tick else None

    async def subscribe(self, ticker: str) -> None:
        await self.add_ticker(ticker)

    async def add_ticker(self, ticker: str) -> None:
        async with self._lock:
            if ticker not in self._tickers:
                self._tickers.append(ticker)

    async def remove_ticker(self, ticker: str) -> None:
        async with self._lock:
            if ticker in self._tickers:
                self._tickers.remove(ticker)
            self._latest.pop(ticker, None)

    async def get_prices(self) -> list[PriceTick]:
        """Refresh prices from the API and return the latest tick per ticker.

        Tickers that fail to refresh keep their last known tick.
        """
        async with self._lock:
            tickers = list(self._tickers)
        if not tickers:
            return []

        fresh = await asyncio.to_thread(self._fetch_snapshot, tickers)

        async with self._lock:
            for tick in fresh:
                self._latest[tick.ticker] = tick
            return [self._latest[t] for t in tickers if t in self._latest]

    def _fetch_snapshot(self, tickers: list[str]) -> list[PriceTick]:
        query = urllib.parse.urlencode(
            {"tickers": ",".join(tickers), "apiKey": self._api_key}
        )
        url = f"{self._base_url}/v2/snapshot/locale/us/markets/stocks/tickers?{query}"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        return _parse_snapshot(payload)


def _parse_snapshot(payload: dict[str, Any]) -> list[PriceTick]:
    """Convert a snapshot response into PriceTicks, skipping malformed entries."""
    ticks: list[PriceTick] = []
    for item in payload.get("tickers", []) or []:
        symbol = item.get("ticker")
        last_trade = item.get("lastTrade") or {}
        price = last_trade.get("p", item.get("day", {}).get("c") if isinstance(item.get("day"), dict) else None)
        if not symbol or price is None:
            continue
        timestamp_ns = last_trade.get("t")
        if isinstance(timestamp_ns, int):
            timestamp = datetime.fromtimestamp(timestamp_ns / 1e9, tz=timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)
        ticks.append(PriceTick(ticker=symbol, price=float(price), timestamp=timestamp))
    return ticks