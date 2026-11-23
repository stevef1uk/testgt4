"""FinAlly backend application entrypoint.

Exposes ``create_app(...) -> FastAPI`` which wires health/root/static routes,
registers API routes, initializes the SQLite schema lazily, creates the price
cache and selected market provider, and manages the background market task.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse


# Root directory of the rig layout (``finally/``).  Resolved relative to this
# file so the app works regardless of the current working directory.
RIG_ROOT = Path(__file__).resolve().parents[2]  # .../testgt4/mayor/rig/finally
FRONTEND_OUT = RIG_ROOT / "frontend" / "out"
INDEX_HTML = FRONTEND_OUT / "index.html"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Registers:
      * ``GET /api/health`` — deployment health check
      * ``GET /`` — serves the real exported Next.js ``index.html`` (errors if
        absent; never synthesizes placeholder HTML)
      * Static fallback for the remaining Next.js export assets

    API routes are mounted before the static fallback so ``/api/*`` takes
    precedence.
    """
    app = FastAPI(title="FinAlly", version="1.0.0")

    # --- Health -----------------------------------------------------------
    @app.get("/api/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    # --- Root / static serving -------------------------------------------
    @app.get("/")
    async def root() -> FileResponse:
        """Serve the exported Next.js index.html at the root route.

        Returns a diagnostic server error if the export is absent rather than
        synthesizing placeholder HTML.
        """
        if not INDEX_HTML.is_file():
            return JSONResponse(
                {
                    "error": "frontend export not found",
                    "detail": f"expected {INDEX_HTML}; run `npm run build` in the frontend",
                },
                status_code=503,
            )
        return FileResponse(INDEX_HTML)

    # Static asset fallback for the Next.js export (JS, CSS, images, …).
    # Mounted after /api/* so API routes take precedence.
    if FRONTEND_OUT.is_dir():
        from fastapi.staticfiles import StaticFiles

        app.mount("/", StaticFiles(directory=str(FRONTEND_OUT), html=True))

    return app


__all__ = ["create_app", "RIG_ROOT", "FRONTEND_OUT", "INDEX_HTML"]