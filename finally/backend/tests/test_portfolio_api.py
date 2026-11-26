"""HTTP-level tests for the /api/portfolio routes.

Covers status codes and response shapes for GET /api/portfolio,
GET /api/portfolio/history, and POST /api/portfolio/trades, including the
400 (validation / insufficient funds / oversell) and 404 (no price) paths.
Each test runs against an isolated in-memory SQLite database.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes_portfolio
from app.db.connection import connect
from app.portfolio import engine, repository, snapshots

STARTING_CASH = 10_000.0
PRICES = {"AAPL": 100.0, "MSFT": 50.0}


@pytest.fixture(autouse=True)
def portfolio_env() -> Iterator[None]:
    """Fresh in-memory DB with known cash and a fixed price table per test."""
    repository.set_connection(connect(":memory:"))
    repository.set_cash_balance(STARTING_CASH)
    engine.set_price_source(lambda ticker: PRICES.get(ticker))
    yield
    engine.set_price_source(lambda ticker: None)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(routes_portfolio.router)
    with TestClient(app) as test_client:
        yield test_client


# --- GET /api/portfolio ---------------------------------------------------


def test_get_portfolio_empty_returns_200_with_cash_and_no_positions(client: TestClient) -> None:
    response = client.get("/api/portfolio")

    assert response.status_code == 200
    body = response.json()
    assert body["cash_balance"] == pytest.approx(STARTING_CASH)
    assert body["total_value"] == pytest.approx(STARTING_CASH)
    assert body["positions"] == []


def test_get_portfolio_shape_includes_position_valuation(client: TestClient) -> None:
    client.post("/api/portfolio/trades", json={"ticker": "AAPL", "side": "buy", "quantity": 10})

    response = client.get("/api/portfolio")

    assert response.status_code == 200
    body = response.json()
    assert body["cash_balance"] == pytest.approx(9_000.0)
    assert body["total_value"] == pytest.approx(10_000.0)
    (position,) = body["positions"]
    assert set(position) == {
        "ticker",
        "quantity",
        "avg_cost",
        "current_price",
        "market_value",
        "unrealized_pnl",
    }
    assert position["ticker"] == "AAPL"
    assert position["market_value"] == pytest.approx(1_000.0)
    assert position["unrealized_pnl"] == pytest.approx(0.0)


def test_get_portfolio_returns_404_when_held_ticker_loses_price(client: TestClient) -> None:
    client.post("/api/portfolio/trades", json={"ticker": "AAPL", "side": "buy", "quantity": 1})
    PRICES.pop("AAPL")
    try:
        response = client.get("/api/portfolio")
    finally:
        PRICES["AAPL"] = 100.0

    assert response.status_code == 404
    assert "no price available" in response.json()["detail"]


# --- GET /api/portfolio/history --------------------------------------------


def test_history_empty_returns_200_empty_list(client: TestClient) -> None:
    response = client.get("/api/portfolio/history")

    assert response.status_code == 200
    assert response.json() == []


def test_history_returns_snapshots_in_order(client: TestClient) -> None:
    snapshots.record_portfolio_snapshot()
    client.post("/api/portfolio/trades", json={"ticker": "MSFT", "side": "buy", "quantity": 2})
    snapshots.record_portfolio_snapshot()

    response = client.get("/api/portfolio/history")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    for point in body:
        assert set(point) == {"total_value", "recorded_at"}
        assert isinstance(point["total_value"], float)
        assert isinstance(point["recorded_at"], str)
    assert body[0]["recorded_at"] <= body[1]["recorded_at"]


# --- POST /api/portfolio/trades -------------------------------------------


def test_buy_trade_returns_201_with_trade_shape(client: TestClient) -> None:
    response = client.post(
        "/api/portfolio/trades", json={"ticker": "AAPL", "side": "buy", "quantity": 5}
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "ticker", "side", "quantity", "price", "executed_at"}
    assert body["ticker"] == "AAPL"
    assert body["side"] == "buy"
    assert body["quantity"] == pytest.approx(5.0)
    assert body["price"] == pytest.approx(100.0)
    assert body["id"] > 0


def test_sell_trade_returns_201_and_credits_cash(client: TestClient) -> None:
    client.post("/api/portfolio/trades", json={"ticker": "AAPL", "side": "buy", "quantity": 5})

    response = client.post(
        "/api/portfolio/trades", json={"ticker": "AAPL", "side": "sell", "quantity": 5}
    )

    assert response.status_code == 201
    assert response.json()["side"] == "sell"
    assert client.get("/api/portfolio").json()["cash_balance"] == pytest.approx(STARTING_CASH)


def test_buy_with_insufficient_cash_returns_400(client: TestClient) -> None:
    response = client.post(
        "/api/portfolio/trades", json={"ticker": "AAPL", "side": "buy", "quantity": 101}
    )

    assert response.status_code == 400
    assert "insufficient cash" in response.json()["detail"]
    assert client.get("/api/portfolio").json()["cash_balance"] == pytest.approx(STARTING_CASH)


def test_oversell_returns_400(client: TestClient) -> None:
    client.post("/api/portfolio/trades", json={"ticker": "AAPL", "side": "buy", "quantity": 2})

    response = client.post(
        "/api/portfolio/trades", json={"ticker": "AAPL", "side": "sell", "quantity": 3}
    )

    assert response.status_code == 400
    assert "insufficient shares" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"ticker": "AAPL", "side": "hold", "quantity": 1},
        {"ticker": "AAPL", "side": "buy", "quantity": 0},
        {"ticker": "", "side": "buy", "quantity": 1},
    ],
)
def test_invalid_trade_payload_returns_400(client: TestClient, payload: dict) -> None:
    response = client.post("/api/portfolio/trades", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"]


def test_trade_for_unpriced_ticker_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/portfolio/trades", json={"ticker": "ZZZZ", "side": "buy", "quantity": 1}
    )

    assert response.status_code == 404
    assert "no price available" in response.json()["detail"]