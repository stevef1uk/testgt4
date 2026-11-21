import asyncio
import inspect
import os
from contextlib import suppress
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .market.cache import MarketCache
from .market.gbm import GBMProvider
from .market.massive import MassiveProvider

_frontend = Path(__file__).resolve().parents[2] / "frontend" / "out"
TICKERS = ("AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "NFLX")


def _make_provider() -> Any:
    if os.getenv("MARKET_PROVIDER", "gbm").lower() == "massive":
        return MassiveProvider()
    return GBMProvider()


def _snapshot(cache: Any) -> dict[str, Any]:
    for name in ("snapshot", "get_all", "all"):
        method = getattr(cache, name, None)
        if callable(method):
            value = method()
            return value if isinstance(value, dict) else {"prices": value}
    if isinstance(cache, dict):
        return dict(cache)
    return {}


def _event_stream(cache: Any):
    async def stream():
        while True:
            payload = _snapshot(cache)
            yield f"data: {__import__('json').dumps(payload)}\\n\\n"
            await asyncio.sleep(1)

    return stream()


def create_app(provider: Any | None = None, cache: Any | None = None) -> FastAPI:
    selected_provider = provider or _make_provider()
    market_cache = cache or MarketCache()
    application = FastAPI(title="FinAlly Trading Dashboard")
    application.state.provider = selected_provider
    application.state.market_cache = market_cache
    application.state.market_task = None

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/api/stream/prices")
    async def prices():
        return StreamingResponse(
            _event_stream(market_cache),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    @application.on_event("startup")
    async def start_market_data() -> None:
        starter = getattr(selected_provider, "start", None)
        if callable(starter):
            result = starter(market_cache, TICKERS)
            if inspect.isawaitable(result):
                result = await result
            if isinstance(result, asyncio.Task):
                application.state.market_task = result

    @application.on_event("shutdown")
    async def stop_market_data() -> None:
        task = application.state.market_task
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        stopper = getattr(selected_provider, "stop", None)
        if callable(stopper):
            result = stopper()
            if inspect.isawaitable(result):
                await result

    @application.get("/{path:path}")
    def frontend(path: str):
        requested = _frontend / path
        if path and requested.is_file():
            return FileResponse(requested)
        index = _frontend / "index.html"
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(status_code=503, detail="Frontend export not found")

    if (_frontend / "_next").is_dir():
        application.mount("/_next", StaticFiles(directory=_frontend / "_next"), name="next-assets")
    return application


app = create_app()