"""Watchlist REST routes for the default user's watchlist.

Rows live in the ``watchlist`` table (see ``app/db/schema.sql``) and are seeded
by ``app/db/seed.py``. Each request opens its own connection so state is never
shared between handlers.
"""

from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator

from app.db.connection import connect, transaction
from app.db.seed import DEFAULT_USER_ID

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

_TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")


class WatchlistAddRequest(BaseModel):
    """Request body for POST /api/watchlist."""

    model_config = ConfigDict(extra="forbid")

    ticker: str

    @field_validator("ticker")
    @classmethod
    def _normalise(cls, value: str) -> str:
        normalised = value.strip().upper()
        if not _TICKER_RE.match(normalised):
            raise ValueError("ticker must be 1-10 characters: letters, digits, '.' or '-'")
        return normalised


def _open() -> Any:
    from app.db.connection import DEFAULT_DB_PATH  # noqa: PLC0415

    return connect(DEFAULT_DB_PATH)


def _list_tickers(conn: Any) -> list[dict[str, str]]:
    rows = conn.execute(
        "SELECT ticker FROM watchlist WHERE user_id = ? ORDER BY rowid",
        (DEFAULT_USER_ID,),
    ).fetchall()
    return [{"ticker": row["ticker"]} for row in rows]


@router.get("", status_code=status.HTTP_200_OK)
def get_watchlist() -> list[dict[str, str]]:
    """Return the default watchlist as a list of ``{"ticker": str}`` objects."""
    conn = _open()
    try:
        return _list_tickers(conn)
    finally:
        conn.close()


@router.post("", status_code=status.HTTP_201_CREATED)
def add_watchlist_ticker(payload: WatchlistAddRequest) -> list[dict[str, str]]:
    """Add a ticker to the default watchlist. Rejects duplicates with 409."""
    conn = _open()
    try:
        with transaction(conn):
            exists = conn.execute(
                "SELECT 1 FROM watchlist WHERE user_id = ? AND ticker = ?",
                (DEFAULT_USER_ID, payload.ticker),
            ).fetchone()
            if exists is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"{payload.ticker} is already in the watchlist",
                )
            conn.execute(
                "INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)",
                (DEFAULT_USER_ID, payload.ticker),
            )
        return _list_tickers(conn)
    finally:
        conn.close()


@router.delete("/{ticker}", status_code=status.HTTP_200_OK)
def remove_watchlist_ticker(ticker: str) -> list[dict[str, str]]:
    """Remove a ticker from the default watchlist. Returns 404 if absent."""
    normalised = ticker.strip().upper()
    conn = _open()
    try:
        with transaction(conn):
            cursor = conn.execute(
                "DELETE FROM watchlist WHERE user_id = ? AND ticker = ?",
                (DEFAULT_USER_ID, normalised),
            )
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{normalised} is not in the watchlist",
                )
        return _list_tickers(conn)
    finally:
        conn.close()