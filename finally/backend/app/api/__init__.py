"""FastAPI route registration for the canonical FinAlly API."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI, status
from fastapi.responses import StreamingResponse

from importlib import import_module

try:
    encode_event = import_module("app.market.sse").encode_event
    _schemas = import_module("app.api.schemas")
except ModuleNotFoundError:
    encode_event = import_module("finally.backend.app.market.sse").encode_event
    _schemas = import_module("finally.backend.app.api.schemas")

ChatRequest = _schemas.ChatRequest
ChatResponse = _schemas.ChatResponse
PortfolioHistory = _schemas.PortfolioHistory
PortfolioResponse = _schemas.PortfolioResponse
TradeRequest = _schemas.TradeRequest
TradeResponse = _schemas.TradeResponse
WatchlistItem = _schemas.WatchlistItem
WatchlistRequest = _schemas.WatchlistRequest


def _health() -> dict[str, str]:
    return {"status": "ok"}


def _prices() -> Iterator[str]:
    yield encode_event(
        {
            "ticker": "AAPL",
            "price": 0.0,
            "previous_price": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "change_direction": "unchanged",
        }
    )


def _portfolio() -> PortfolioResponse:
    return PortfolioResponse(positions=[], cash=0.0, total_value=0.0, unrealized_pnl=0.0)


def _trade(request: TradeRequest) -> TradeResponse:
    return TradeResponse(
        ticker=request.ticker,
        quantity=request.quantity,
        side=request.side,
        price=0.0,
        cash=0.0,
        message="Trade accepted",
    )


def _history() -> PortfolioHistory:
    return PortfolioHistory(snapshots=[])


def _watchlist() -> list[WatchlistItem]:
    return []


def _add_watchlist(request: WatchlistRequest) -> WatchlistItem:
    return WatchlistItem(
        ticker=request.ticker,
        price=0.0,
        timestamp=datetime.now(timezone.utc),
    )


def _remove_watchlist(ticker: str) -> dict[str, str]:
    return {"ticker": ticker, "status": "removed"}


def _chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(message=request.message)


def create_api_router() -> APIRouter:
    """Create the router containing all canonical API endpoints."""
    router = APIRouter(prefix="/api")
    router.add_api_route(
        "/stream/prices",
        _prices,
        methods=["GET"],
        response_class=StreamingResponse,
    )
    router.add_api_route("/portfolio", _portfolio, methods=["GET"], response_model=PortfolioResponse)
    router.add_api_route(
        "/portfolio/trade",
        _trade,
        methods=["POST"],
        response_model=TradeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    router.add_api_route(
        "/portfolio/history",
        _history,
        methods=["GET"],
        response_model=PortfolioHistory,
    )
    router.add_api_route("/watchlist", _watchlist, methods=["GET"])
    router.add_api_route("/watchlist", _add_watchlist, methods=["POST"], response_model=WatchlistItem)
    router.add_api_route("/watchlist/{ticker}", _remove_watchlist, methods=["DELETE"])
    router.add_api_route("/chat", _chat, methods=["POST"], response_model=ChatResponse)
    router.add_api_route("/health", _health, methods=["GET"])
    return router


def register_routes(
    app: FastAPI,
    *,
    router_factory: Callable[[], APIRouter] = create_api_router,
) -> FastAPI:
    """Register canonical API routes on an existing FastAPI application."""
    router = router_factory()
    app.router.routes.extend(router.routes)
    return app


__all__ = ["create_api_router", "register_routes"]