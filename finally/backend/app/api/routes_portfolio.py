"""Portfolio REST routes.

Handlers delegate to ``app.portfolio.engine``. The engine module is imported
lazily inside each handler so this module compiles before the engine bead
(te-5zc) is implemented.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


def _engine() -> Any:
    from app.portfolio import engine  # noqa: PLC0415  (deferred until engine exists)

    return engine


@router.get("", status_code=status.HTTP_200_OK)
def get_portfolio() -> Any:
    """Return current cash, positions, and total portfolio value."""
    try:
        return _engine().get_portfolio_state()
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/history", status_code=status.HTTP_200_OK)
def get_portfolio_history() -> Any:
    """Return recorded portfolio value snapshots in chronological order."""
    return _engine().get_portfolio_history()


@router.post("/trades", status_code=status.HTTP_201_CREATED)
def post_trade(payload: dict[str, Any]) -> Any:
    """Execute a buy/sell trade against the simulated portfolio."""
    try:
        return _engine().execute_trade(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc