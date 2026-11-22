"""FastAPI route registration for the canonical FinAlly API."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, FastAPI


_CANONICAL_PATHS = (
    "/stream/prices",
    "/portfolio",
    "/portfolio/trade",
    "/portfolio/history",
    "/watchlist",
    "/watchlist/{ticker}",
    "/chat",
    "/health",
)


def create_api_router() -> APIRouter:
    """Create the router containing the canonical API route boundary."""
    router = APIRouter(prefix="/api")
    for path in _CANONICAL_PATHS:
        router.add_api_route(path, _route_placeholder, methods=["GET"])
    return router


def _route_placeholder() -> None:
    """Provide route ownership until application handlers are registered."""
    return None


def register_routes(
    app: FastAPI,
    *,
    router_factory: Callable[[], APIRouter] = create_api_router,
) -> FastAPI:
    """Attach every factory-produced route to the application."""
    router = router_factory()
    for route in router.routes:
        app.add_api_route(
            route.path,
            route.endpoint,
            methods=list(route.methods or {"GET"}),
            name=route.name,
            include_in_schema=route.include_in_schema,
        )
    return app


__all__ = ["create_api_router", "register_routes"]