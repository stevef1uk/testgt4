from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.db.schema import DEFAULT_CASH, DEFAULT_TICKERS, initialize_database


def test_initialize_database_is_idempotent_and_seeds_spec_defaults() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        initialize_database(connection)
        initialize_database(connection)

        assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)
        assert connection.execute(
            "SELECT cash FROM users WHERE id = 1"
        ).fetchone() == (DEFAULT_CASH,)
        assert tuple(
            row[0]
            for row in connection.execute(
                "SELECT ticker FROM watchlist ORDER BY rowid"
            )
        ) == DEFAULT_TICKERS
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='positions'"
        ).fetchone() == ("positions",)
    finally:
        connection.close()