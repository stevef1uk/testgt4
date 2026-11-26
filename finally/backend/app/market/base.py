"""Abstract market data source interface and shared tick model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class PriceTick:
    """A single price observation for one ticker per SPEC Section 6."""

    ticker: str
    price: float
    previous_price: float | None = None
    change: float = 0.0
    change_percent: float = 0.0
    change_direction: str = "flat"  # "up" | "down" | "flat"
    timestamp: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self.ticker:
            raise ValueError("ticker must be non-empty")
        if self.price < 0:
            raise ValueError("price must be non-negative")
        if self.change_direction not in {"up", "down", "flat"}:
            raise ValueError("change_direction must be 'up', 'down', or 'flat'")


class MarketDataSource(ABC):
    """Common interface for market data providers per architecture.md."""

    @abstractmethod
    async def start(self, tickers: list[str]) -> None:
        """Begin producing prices for the given tickers."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop producing prices and release resources."""

    @abstractmethod
    async def get_price(self, ticker: str) -> float | None:
        """Return the current price for a single ticker."""

    @abstractmethod
    async def subscribe(self, ticker: str) -> None:
        """Subscribe to an additional ticker."""

    async def add_ticker(self, ticker: str) -> None:
        """Alias for subscribe."""
        await self.subscribe(ticker)

    @abstractmethod
    async def remove_ticker(self, ticker: str) -> None:
        """Stop tracking a ticker."""

    @abstractmethod
    async def get_prices(self) -> list[PriceTick]:
        """Return the latest tick for every tracked ticker."""


# Backwards compatibility alias
PriceSource = MarketDataSource
