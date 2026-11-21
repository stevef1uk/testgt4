"""FastAPI route registration for the canonical FinAlly API."""

from __future__ import annotations

from collections.abc import Callable
from fastapi import APIRouter, FastAPI

from . import schemas


def create_api_router() -> APIRouter:
    """Create the API router; application handlers are registered by main."""
    return APIRouter(prefix="/api")


def register_routes(
    app: FastAPI,
    *,
    router_factory: Callable[[], APIRouter] = create_api_router,
) -> FastAPI:
    """Attach the supplied router using FastAPI's supported registration API."""
    app.include_router(router_factory())
    return app


__all__ = ["create_api_router", "register_routes"]