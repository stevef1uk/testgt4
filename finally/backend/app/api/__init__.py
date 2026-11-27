"""API package for the StockPilot backend.

Exposes the APIRouter (GET /api/health only in this phase) and the
create_app() factory. Later phases register portfolio, watchlist, and chat
routers from their own modules.
"""

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import StreamingResponse

from app.api.routes_chat import router as chat_router
from app.market.stream import price_events
from app.market.cache import PriceCache
from app.api.routes_portfolio import router as portfolio_router
from app.api.routes_watchlist import router as watchlist_router

router = APIRouter()
stream_router = APIRouter(prefix="/api/stream", tags=["stream"])


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
    app = FastAPI(title=title, version=version)
    app.include_router(router)
    app.include_router(watchlist_router)
    app.include_router(portfolio_router)
    app.state.price_cache = PriceCache()
    app.include_router(chat_router)
    app.include_router(stream_router)
    return app