"""Background loop that polls a PriceSource and feeds the PriceCache."""

from __future__ import annotations

import asyncio
import logging

from app.market.base import PriceSource
from app.market.cache import PriceCache

logger = logging.getLogger(__name__)


class PricePoller:
    """Periodically pulls prices from a PriceSource and stores them in a PriceCache."""

    def __init__(
        self,
        source: PriceSource,
        cache: PriceCache,
        interval: float = 0.5,
    ) -> None:
        if interval <= 0:
            raise ValueError("interval must be positive")
        self._source = source
        self._cache = cache
        self._interval = interval
        self._task: asyncio.Task[None] | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self, tickers: list[str]) -> None:
        """Start the source for the given tickers and begin the polling loop."""
        if self.running:
            return
        await self._source.start(tickers)
        self._task = asyncio.create_task(self._run(), name="price-poller")

    async def stop(self) -> None:
        """Cancel the polling loop and stop the source. Safe to call repeatedly."""
        task = self._task
        self._task = None
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await self._source.stop()

    async def poll_once(self) -> int:
        """Fetch one batch of prices into the cache. Returns the number stored."""
        ticks = await self._source.get_prices()
        for tick in ticks:
            await self._cache.update(tick)
        return len(ticks)

    async def _run(self) -> None:
        while True:
            try:
                await self.poll_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("price poll failed; retrying next interval")
            await asyncio.sleep(self._interval)