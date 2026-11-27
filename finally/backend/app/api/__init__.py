"""API package for the StockPilot backend.

Exposes the APIRouter (GET /api/health), routes, and the create_app() factory.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import StreamingResponse

from app.api.routes_chat import router as chat_router
from app.api.routes_portfolio import router as portfolio_router
from app.api.routes_watchlist import router as watchlist_router
from app.market.base import PriceTick
from app.market.cache import PriceCache
from app.market.massive_client import MassiveClient
from app.market.poller import PricePoller
from app.market.simulator import SimulatedPriceSource
from app.market.stream import price_events
from app.portfolio import engine as portfolio_engine

router = APIRouter()
stream_router = APIRouter(prefix="/api/stream", tags=["stream"])

DEFAULT_TICKERS = [
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "NFLX",
]

DEFAULT_START_PRICES = {
    "AAPL": 190.50,
    "GOOGL": 175.00,
    "MSFT": 420.00,
    "AMZN": 185.00,
    "TSLA": 210.00,
    "NVDA": 125.00,
    "META": 500.00,
    "JPM": 200.00,
    "V": 275.00,
    "NFLX": 650.00,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = app.state.price_cache
    massive_key = os.getenv("MASSIVE_API_KEY", "").strip()
    if massive_key:
        source = MassiveClient(api_key=massive_key)
    else:
        source = SimulatedPriceSource(start_prices=DEFAULT_START_PRICES)

    poller = PricePoller(source, cache, interval=1.0)
    await poller.start(DEFAULT_TICKERS)
    await poller.poll_once()
    app.state.price_poller = poller

    def _lookup_price(ticker: str) -> float | None:
        if ticker in cache._ticks:
            return cache._ticks[ticker].price
        return None

    portfolio_engine.set_price_source(_lookup_price)

    yield

    await poller.stop()


@stream_router.get("/prices")
async def stream_prices(request: Request) -> StreamingResponse:
    """Stream price updates as text/event-stream frames per SPEC Section 6."""
    cache = request.app.state.price_cache
    return StreamingResponse(
        price_events(cache),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app(title: str = "StockPilot", version: str = "0.1.0") -> FastAPI:
    cache = PriceCache()
    for ticker, price in DEFAULT_START_PRICES.items():
        cache._ticks[ticker] = PriceTick(ticker=ticker, price=price)
        cache._previous_prices[ticker] = price

    portfolio_engine.set_price_source(
        lambda t: cache._ticks[t].price if t in cache._ticks else None
    )

    app = FastAPI(title=title, version=version, lifespan=lifespan)
    app.state.price_cache = cache
    app.include_router(router)
    app.include_router(watchlist_router)
    app.include_router(portfolio_router)
    app.include_router(chat_router)
    app.include_router(stream_router)
    return app