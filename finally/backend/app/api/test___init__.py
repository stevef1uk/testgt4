from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api import register_routes


def test_register_routes_exposes_canonical_api_paths() -> None:
    app = FastAPI()
    register_routes(app)

    paths = {
        route.path
        for route in app.routes
        if isinstance(route, APIRoute)
    }

    assert paths == {
        "/api/stream/prices",
        "/api/portfolio",
        "/api/portfolio/trade",
        "/api/portfolio/history",
        "/api/watchlist",
        "/api/watchlist/{ticker}",
        "/api/chat",
        "/api/health",
    }