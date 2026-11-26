"""Idempotent seed for the FinAlly SQLite database.

Creates the default user profile and default watchlist. Safe to run on every
startup: existing rows are left untouched.
"""

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

DEFAULT_USER_ID = "default"
DEFAULT_CASH_BALANCE = 10000.0
DEFAULT_WATCHLIST = [
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
]


def apply_schema(conn: sqlite3.Connection) -> None:
    """Run schema.sql (idempotent DDL)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def seed_default_data(conn: sqlite3.Connection) -> None:
    """Insert the default profile and watchlist if they are missing."""
    conn.execute(
        "INSERT OR IGNORE INTO users_profile (id, cash_balance) VALUES (?, ?)",
        (DEFAULT_USER_ID, DEFAULT_CASH_BALANCE),
    )
    conn.executemany(
        "INSERT OR IGNORE INTO watchlist (user_id, ticker) VALUES (?, ?)",
        [(DEFAULT_USER_ID, ticker) for ticker in DEFAULT_WATCHLIST],
    )
    conn.commit()


def initialize_database(db_path: str) -> None:
    """Create schema and seed default data at db_path."""
    conn = sqlite3.connect(db_path)
    try:
        apply_schema(conn)
        seed_default_data(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    import os

    initialize_database(os.environ.get("DB_PATH", "finally.db"))