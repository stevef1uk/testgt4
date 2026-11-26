"""SQLite persistence for portfolio state: cash, positions, trades, snapshots.

The connection is created lazily against ``app.db.connection.DEFAULT_DB_PATH``
and the idempotent ``schema.sql`` is applied on first use. Tests can inject a
connection with ``set_connection``.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.db.connection import DEFAULT_DB_PATH, connect

USER_ID = "default"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "schema.sql"

_conn: sqlite3.Connection | None = None


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("INSERT OR IGNORE INTO users_profile (id) VALUES (?)", (USER_ID,))
    conn.commit()


def set_connection(conn: sqlite3.Connection) -> None:
    """Install the connection used by all repository functions (also applies schema)."""
    global _conn
    _ensure_schema(conn)
    _conn = conn


def _db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        set_connection(connect(DEFAULT_DB_PATH))
    assert _conn is not None
    return _conn


def get_cash_balance(default: float = 0.0) -> float:
    row = _db().execute(
        "SELECT cash_balance FROM users_profile WHERE id = ?", (USER_ID,)
    ).fetchone()
    return float(row["cash_balance"]) if row else float(default)


def set_cash_balance(amount: float) -> None:
    conn = _db()
    conn.execute(
        "UPDATE users_profile SET cash_balance = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') "
        "WHERE id = ?",
        (float(amount), USER_ID),
    )
    conn.commit()


def list_positions() -> list[dict[str, Any]]:
    rows = _db().execute(
        "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? ORDER BY ticker",
        (USER_ID,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_position(ticker: str) -> dict[str, Any] | None:
    row = _db().execute(
        "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?",
        (USER_ID, ticker),
    ).fetchone()
    return dict(row) if row else None


def upsert_position(ticker: str, quantity: float, avg_cost: float) -> None:
    conn = _db()
    conn.execute(
        "INSERT INTO positions (user_id, ticker, quantity, avg_cost) VALUES (?, ?, ?, ?) "
        "ON CONFLICT (user_id, ticker) DO UPDATE SET "
        "quantity = excluded.quantity, avg_cost = excluded.avg_cost, "
        "updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')",
        (USER_ID, ticker, float(quantity), float(avg_cost)),
    )
    conn.commit()


def delete_position(ticker: str) -> None:
    conn = _db()
    conn.execute("DELETE FROM positions WHERE user_id = ? AND ticker = ?", (USER_ID, ticker))
    conn.commit()


def record_trade(
    *,
    ticker: str,
    side: str,
    quantity: float,
    price: float,
    executed_at: datetime,
) -> dict[str, Any]:
    conn = _db()
    cur = conn.execute(
        "INSERT INTO trades (user_id, ticker, side, quantity, price, executed_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (USER_ID, ticker, side, float(quantity), float(price), executed_at.isoformat()),
    )
    conn.commit()
    return {
        "id": int(cur.lastrowid),
        "ticker": ticker,
        "side": side,
        "quantity": float(quantity),
        "price": float(price),
        "executed_at": executed_at.isoformat(),
    }


def record_snapshot(total_value: float) -> None:
    conn = _db()
    conn.execute(
        "INSERT INTO portfolio_snapshots (user_id, total_value) VALUES (?, ?)",
        (USER_ID, float(total_value)),
    )
    conn.commit()


def list_snapshots() -> list[dict[str, Any]]:
    rows = _db().execute(
        "SELECT total_value, recorded_at FROM portfolio_snapshots "
        "WHERE user_id = ? ORDER BY recorded_at, id",
        (USER_ID,),
    ).fetchall()
    return [{"total_value": float(r["total_value"]), "recorded_at": r["recorded_at"]} for r in rows]