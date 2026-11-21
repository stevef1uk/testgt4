from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import TypeAlias

Connection: TypeAlias = sqlite3.Connection

DEFAULT_TICKERS = (
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
DEFAULT_CASH = 10_000.0


def database_path() -> Path:
    """Return the configured SQLite path, defaulting to the checked-in db directory."""
    configured = os.getenv("DATABASE_URL", "")
    if configured.startswith("sqlite:///"):
        configured = configured.removeprefix("sqlite:///")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "db" / "app.db"


def initialize_database(connection: Connection) -> None:
    """Create the single-user schema and seed its initial account idempotently."""
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            cash REAL NOT NULL CHECK (cash >= 0)
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            ticker TEXT PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS positions (
            ticker TEXT PRIMARY KEY,
            shares REAL NOT NULL DEFAULT 0 CHECK (shares >= 0),
            average_cost REAL NOT NULL DEFAULT 0 CHECK (average_cost >= 0)
        );

        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            quantity REAL NOT NULL CHECK (quantity > 0),
            side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
            price REAL NOT NULL CHECK (price >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_value REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO users (id, cash) VALUES (1, ?)",
        (DEFAULT_CASH,),
    )
    connection.executemany(
        "INSERT OR IGNORE INTO watchlist (ticker) VALUES (?)",
        ((ticker,) for ticker in DEFAULT_TICKERS),
    )
    connection.commit()