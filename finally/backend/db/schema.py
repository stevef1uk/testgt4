"""SQLite schema for the FinAlly database and portfolio engine.

Creates all tables idempotently. Uses only the standard library.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_CASH_BALANCE: float = 10_000.0
DEFAULT_USER_ID: str = "default"

DEFAULT_WATCHLIST: tuple[str, ...] = (
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "NFLX",
)

SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS users_profile (
        id TEXT PRIMARY KEY,
        cash_balance REAL NOT NULL DEFAULT 10000.0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS watchlist (
        user_id TEXT NOT NULL,
        ticker TEXT NOT NULL,
        added_at TEXT NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, ticker),
        FOREIGN KEY (user_id) REFERENCES users_profile (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS positions (
        user_id TEXT NOT NULL,
        ticker TEXT NOT NULL,
        quantity REAL NOT NULL DEFAULT 0,
        avg_cost REAL NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        PRIMARY KEY (user_id, ticker),
        FOREIGN KEY (user_id) REFERENCES users_profile (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        ticker TEXT NOT NULL,
        side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
        quantity REAL NOT NULL CHECK (quantity > 0),
        price REAL NOT NULL CHECK (price > 0),
        executed_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users_profile (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS portfolio_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        total_value REAL NOT NULL,
        recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users_profile (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users_profile (id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_trades_user_ticker
        ON trades (user_id, ticker)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_snapshots_user_time
        ON portfolio_snapshots (user_id, recorded_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chat_user_time
        ON chat_messages (user_id, created_at)
    """,
)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes on an open connection. Idempotent."""
    conn.execute("PRAGMA foreign_keys = ON")
    for statement in SCHEMA_STATEMENTS:
        conn.execute(statement)
    conn.commit()


def seed_default_user(conn: sqlite3.Connection) -> None:
    """Insert the default user with starting cash and default watchlist. Idempotent."""
    conn.execute(
        "INSERT OR IGNORE INTO users_profile (id, cash_balance) VALUES (?, ?)",
        (DEFAULT_USER_ID, DEFAULT_CASH_BALANCE),
    )
    conn.executemany(
        "INSERT OR IGNORE INTO watchlist (user_id, ticker) VALUES (?, ?)",
        [(DEFAULT_USER_ID, ticker) for ticker in DEFAULT_WATCHLIST],
    )
    conn.commit()


def get_db_connection(db_path: str | Path) -> sqlite3.Connection:
    """Open a connection to the database (creating parent directories as needed).

    Ensures the schema exists and defaults are seeded before returning.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    seed_default_user(conn)
    return conn


def init_db(db_path: str | Path) -> None:
    """Create the schema and seed defaults at ``db_path``. Idempotent; returns nothing."""
    conn = get_db_connection(db_path)
    conn.close()