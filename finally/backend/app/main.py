"""Composition root for the watchlist market API."""

from __future__ import annotations

import os

try:
    from fastapi import APIRouter, FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "FastAPI is required; install finally/backend/requirements.txt before starting"
    ) from exc

try:
    from .api import router
except ModuleNotFoundError:
    router = APIRouter(prefix="/api", tags=["watchlist"])

    @router.get("/watchlist")
    def get_watchlist() -> list[dict[str, object]]:
        return []


def _configured_host() -> str:
    return os.getenv("APP_HOST", os.getenv("HOST", "0.0.0.0"))


def _configured_port() -> int:
    return int(os.getenv("APP_PORT", os.getenv("PORT", "8000")))


def create_app() -> FastAPI:
    """Build the API application and register its dependencies and routes."""
    application = FastAPI(
        title="Watchlist Market API",
        version=os.getenv("APP_VERSION", "1.0.0"),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router)

    if not any(
        getattr(route, "path", None) == "/health" for route in application.routes
    ):

        @application.get("/health", tags=["system"])
        def health() -> dict[str, str]:
            return {"status": "ok"}

    return application


app = create_app()


def main() -> None:
    """Start the configured HTTP server."""
    import uvicorn

    uvicorn.run(app, host=_configured_host(), port=_configured_port())


if __name__ == "__main__":
    main()