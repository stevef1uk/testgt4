"""API tests for the watchlist routes (te-8sc).

Each test gets an isolated SQLite database under ``tmp_path``. The database is
created from ``app/db/schema.sql`` and seeded through ``app/db/seed.py``, so
the assertions run against the same seed data the app ships with.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.db.connection as connection_module
from app.api import routes_watchlist
from app.db import seed as seed_module
from app.db.connection import connect

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "app" / "db" / "schema.sql"
SEEDED = list(seed_module.DEFAULT_WATCHLIST)


def _seed_function():
    """Return the seeding callable exported by app.db.seed."""
    for name in dir(seed_module):
        if name.startswith("seed") and callable(getattr(seed_module, name)):
            return getattr(seed_module, name)
    pytest.fail("app/db/seed.py exports no callable starting with 'seed'")


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    db_path = tmp_path / "finally.db"
    monkeypatch.setattr(connection_module, "DEFAULT_DB_PATH", db_path)

    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _seed_function()(conn)
        conn.commit()
    finally:
        conn.close()

    api = FastAPI()
    api.include_router(routes_watchlist.router)
    with TestClient(api) as test_client:
        yield test_client


def _tickers(client: TestClient) -> list[str]:
    response = client.get("/api/watchlist")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all(set(item.keys()) == {"ticker"} for item in body)
    return [item["ticker"] for item in body]


def test_get_returns_ten_seeded_tickers_with_shape(client: TestClient) -> None:
    response = client.get("/api/watchlist")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 10
    assert all(isinstance(item, dict) and set(item) == {"ticker"} for item in body)
    assert {item["ticker"] for item in body} == set(SEEDED)


def test_post_adds_new_ticker_and_get_includes_it(client: TestClient) -> None:
    response = client.post("/api/watchlist", json={"ticker": "PYPL"})

    assert response.status_code == 201
    assert {"ticker": "PYPL"} in response.json()
    assert "PYPL" in _tickers(client)
    assert len(_tickers(client)) == 11


def test_post_normalises_ticker_case_and_whitespace(client: TestClient) -> None:
    response = client.post("/api/watchlist", json={"ticker": "  pypl  "})

    assert response.status_code == 201
    assert "PYPL" in _tickers(client)


def test_post_duplicate_is_rejected_and_list_unchanged(client: TestClient) -> None:
    before = _tickers(client)

    response = client.post("/api/watchlist", json={"ticker": "AAPL"})

    assert response.status_code == 409
    assert _tickers(client) == before
    assert len(before) == 10


def test_post_invalid_ticker_is_rejected_and_list_unchanged(client: TestClient) -> None:
    before = _tickers(client)

    response = client.post("/api/watchlist", json={"ticker": "not a ticker!"})

    assert response.status_code == 422
    assert _tickers(client) == before


def test_delete_removes_ticker_and_get_no_longer_includes_it(client: TestClient) -> None:
    response = client.delete("/api/watchlist/TSLA")

    assert response.status_code == 200
    assert "TSLA" not in [item["ticker"] for item in response.json()]
    assert "TSLA" not in _tickers(client)
    assert len(_tickers(client)) == 9


def test_delete_missing_ticker_returns_404_and_list_unchanged(client: TestClient) -> None:
    before = _tickers(client)

    response = client.delete("/api/watchlist/ZZZZ")

    assert response.status_code == 404
    assert _tickers(client) == before