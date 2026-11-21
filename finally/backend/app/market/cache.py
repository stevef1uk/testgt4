"""Thread-safe in-memory cache for latest market prices."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock


@dataclass(frozen=True, slots=True)
class PriceSnapshot:
    ticker: str
    price: float
    previous_price: float | None
    timestamp: datetime


class MarketCache:
    """Store the latest and previous price for each ticker."""

    def __init__(self) -> None:
        self._values: dict[str, PriceSnapshot] = {}
        self._lock = RLock()

    def update(
        self,
        ticker: str,
        price: float,
        *,
        timestamp: datetime | None = None,
    ) -> PriceSnapshot:
        if not ticker:
            raise ValueError("ticker must not be empty")
        if price < 0:
            raise ValueError("price must be non-negative")

        observed_at = timestamp or datetime.now(timezone.utc)
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)

        with self._lock:
            prior = self._values.get(ticker)
            snapshot = PriceSnapshot(
                ticker=ticker,
                price=float(price),
                previous_price=prior.price if prior is not None else None,
                timestamp=observed_at,
            )
            self._values[ticker] = snapshot
            return snapshot

    def get(self, ticker: str) -> PriceSnapshot | None:
        with self._lock:
            return self._values.get(ticker)

    def latest(self, ticker: str) -> PriceSnapshot | None:
        return self.get(ticker)

    def previous(self, ticker: str) -> float | None:
        snapshot = self.get(ticker)
        return snapshot.previous_price if snapshot is not None else None

    def all(self) -> dict[str, PriceSnapshot]:
        with self._lock:
            return dict(self._values)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()