"""API package for the StockPilot backend.

Exposes the APIRouter (GET /api/health only in this phase) and the
create_app() factory. Later phases register portfolio, watchlist, and chat
routers from their own modules.
"""

from fastapi import APIRouter, FastAPI

from app.api.routes_chat import router as chat_router
from app.api.routes_portfolio import router as portfolio_router
from app.api.routes_watchlist import router as watchlist_router

router = APIRouter()


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app(title: str = "StockPilot", version: str = "0.1.0") -> FastAPI:
    app = FastAPI(title=title, version=version)
    app.include_router(router)
    app.include_router(watchlist_router)
    app.include_router(portfolio_router)
    app.include_router(chat_router)
    return app