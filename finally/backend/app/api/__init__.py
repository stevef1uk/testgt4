"""FastAPI router for the watchlist market API boundary."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health", tags=["system"], status_code=200, response_model=dict[str, str])
def health() -> dict[str, str]:
    """Report that the API process is ready to receive requests."""
    return {"status": "ok"}


__all__ = ["health", "router"]