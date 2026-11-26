"""Schema and seed tests for the FinAlly SQLite database."""

import sqlite3
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.db import seed  # noqa: E402

SCHEMA_PATH = BACKEND_DIR / "app" / "db" / "schema.sql"

EXPECTED_TABLES = {
    "users_profile",
    "watchlist",
    "positions",
    "trades",
    "portfolio_snapshots",
    "chat_messages",
}


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


def _table_names(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row["name"] for row in rows}


def test_schema_file_exists():
    assert SCHEMA_PATH.is_file()


def test_schema_creates_all_tables(conn):
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert EXPECTED_TABLES <= _table_names(conn)


def test_schema_is_idempotent(conn):
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.executescript(sql)  # second run must not raise
    assert EXPECTED_TABLES <= _table_names(conn)


def test_trades_side_constraint_rejects_invalid_value(conn):
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("INSERT INTO users_profile (id) VALUES ('default')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO trades (user_id, ticker, side, quantity, price) "
            "VALUES ('default', 'AAPL', 'hold', 1, 10)"
        )


def test_watchlist_rejects_duplicate_user_ticker(conn):
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("INSERT INTO users_profile (id) VALUES ('default')")
    conn.execute(
        "INSERT INTO watchlist (user_id, ticker) VALUES ('default', 'AAPL')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO watchlist (user_id, ticker) VALUES ('default', 'AAPL')"
        )


def test_positions_rejects_duplicate_user_ticker(conn):
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("INSERT INTO users_profile (id) VALUES ('default')")
    conn.execute(
        "INSERT INTO positions (user_id, ticker, quantity, avg_cost) "
        "VALUES ('default', 'AAPL', 1, 10)"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO positions (user_id, ticker, quantity, avg_cost) "
            "VALUES ('default', 'AAPL', 2, 11)"
        )


def test_seed_creates_default_profile_and_watchlist(conn):
    seed.apply_schema(conn)
    seed.seed_default_data(conn)

    profile = conn.execute(
        "SELECT cash_balance FROM users_profile WHERE id = ?", (seed.DEFAULT_USER_ID,)
    ).fetchone()
    assert profile is not None
    assert profile["cash_balance"] == pytest.approx(10000.0)

    tickers = {
        row["ticker"]
        for row in conn.execute(
            "SELECT ticker FROM watchlist WHERE user_id = ?", (seed.DEFAULT_USER_ID,)
        )
    }
    assert tickers == set(seed.DEFAULT_WATCHLIST)


def test_seed_is_idempotent(conn):
    seed.apply_schema(conn)
    seed.seed_default_data(conn)
    seed.seed_default_data(conn)

    count = conn.execute("SELECT COUNT(*) AS n FROM watchlist").fetchone()["n"]
    assert count == len(seed.DEFAULT_WATCHLIST)