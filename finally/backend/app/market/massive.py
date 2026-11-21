"""Massive market-data provider adapter."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True, slots=True)
class MarketQuote:
    ticker: str
    price: float
    timestamp: str | None = None


class MassiveProvider:
    """Fetch normalized latest quotes from the Massive REST API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.massive.com",
        timeout: float = 5.0,
        opener: Callable[..., object] | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._opener = opener or urlopen

    def quote(self, ticker: str) -> MarketQuote:
        if not ticker:
            raise ValueError("ticker must not be empty")

        query = urlencode({"ticker": ticker.upper(), "apiKey": self.api_key})
        request = Request(
            f"{self.base_url}/v2/last/trade/{ticker.upper()}?{query}",
            headers={"Accept": "application/json"},
        )
        with self._opener(request, timeout=self.timeout) as response:
            payload = json.loads(response.read())

        return self.normalize_quote(ticker, payload)

    @staticmethod
    def normalize_quote(ticker: str, payload: dict[str, object]) -> MarketQuote:
        result = payload.get("results", payload)
        if not isinstance(result, dict):
            raise ValueError("Massive response has no quote result")

        raw_price = result.get("price", result.get("p"))
        if raw_price is None:
            raise ValueError("Massive response has no price")

        price = float(raw_price)
        if price < 0:
            raise ValueError("Massive quote price must be non-negative")

        raw_timestamp = result.get("timestamp", result.get("t"))
        timestamp = str(raw_timestamp) if raw_timestamp is not None else None
        return MarketQuote(ticker=ticker.upper(), price=price, timestamp=timestamp)