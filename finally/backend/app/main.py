"""FastAPI application entry point for the StockPilot backend.

Later phases register the portfolio, watchlist, and chat routers here.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api import create_app as build_api_app

FRONTEND_INDEX = Path(__file__).resolve().parents[2] / "frontend" / "out" / "index.html"


def create_app(title: str = "StockPilot", version: str = "0.1.0") -> FastAPI:
    app = build_api_app(title=title, version=version)

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        if not FRONTEND_INDEX.is_file():
            return HTMLResponse(
                status_code=503,
                content=(
                    "Frontend export missing at frontend/out/index.html. "
                    "Run `npm run build` in finally/frontend."
                ),
            )
        return HTMLResponse(FRONTEND_INDEX.read_text(encoding="utf-8"))

    return app


app = create_app()