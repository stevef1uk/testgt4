"""Abstract price source interface and shared tick model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class PriceTick:
    """A single price observation for one ticker."""

    ticker: str
    price: float
    timestamp: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self.ticker:
            raise ValueError("ticker must be non-empty")
        if self.price < 0:
            raise ValueError("price must be non-negative")


class PriceSource(ABC):
    """Common interface for market data providers (simulator or live API)."""

    @abstractmethod
    async def start(self, tickers: list[str]) -> None:
        """Begin producing prices for the given tickers."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop producing prices and release resources."""

    @abstractmethod
    async def add_ticker(self, ticker: str) -> None:
        """Start tracking an additional ticker."""

    @abstractmethod
    async def remove_ticker(self, ticker: str) -> None:
        """Stop tracking a ticker."""

    @abstractmethod
    async def get_prices(self) -> list[PriceTick]:
        """Return the latest tick for every tracked ticker."""