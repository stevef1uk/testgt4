import importlib

from fastapi import FastAPI
from fastapi.routing import APIRoute


def test_register_routes_exposes_canonical_api_paths() -> None:
    register_routes = importlib.import_module("finally.backend.app.api").register_routes
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