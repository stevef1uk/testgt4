"""Thread-safe in-memory latest-price cache shared by market data sources and SSE streaming."""

from threading import Lock


class MarketCache:
    """Holds the latest price per ticker. No database access."""

    def __init__(self) -> None:
        self._prices: dict[str, float] = {}
        self._lock = Lock()

    def update(self, ticker: str, price: float) -> None:
        with self._lock:
            self._prices[ticker] = price

    def get(self, ticker: str) -> float | None:
        with self._lock:
            return self._prices.get(ticker)

    def get_latest(self, ticker: str) -> float | None:
        """Architecture contract name for the latest price lookup."""
        return self.get(ticker)

    def snapshot(self) -> dict[str, float]:
        with self._lock:
            return dict(self._prices)


# The test suite and earlier callers use the PriceCache name for the same class.
PriceCache = MarketCache