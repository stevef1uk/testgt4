"""End-to-end trading flow tests for the portfolio routes.

Drives buy and sell through POST /api/portfolio/trades and checks cash and
positions via GET /api/portfolio (architecture: testing section for trading
flow). Each test runs against an isolated in-memory SQLite database.

Acceptance covered:
- A buy reduces cash and creates a position.
- A full sell removes the position and restores cash.
- Selling more than held is rejected.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes_portfolio
from app.db.connection import connect
from app.portfolio import engine, repository

STARTING_CASH = 10_000.0
PRICES = {"AAPL": 100.0}


@pytest.fixture(autouse=True)
def trading_env() -> Iterator[None]:
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


def _trade(client: TestClient, side: str, quantity: float) -> object:
    return client.post(
        "/api/portfolio/trades",
        json={"ticker": "AAPL", "side": side, "quantity": quantity},
    )


def test_buy_reduces_cash_and_creates_position(client: TestClient) -> None:
    response = _trade(client, "buy", 10)

    assert response.status_code == 201

    portfolio = client.get("/api/portfolio").json()
    assert portfolio["cash_balance"] == pytest.approx(STARTING_CASH - 10 * 100.0)
    assert len(portfolio["positions"]) == 1
    (position,) = portfolio["positions"]
    assert position["ticker"] == "AAPL"
    assert position["quantity"] == pytest.approx(10.0)
    assert position["avg_cost"] == pytest.approx(100.0)
    assert position["market_value"] == pytest.approx(1_000.0)


def test_full_sell_removes_position_and_restores_cash(client: TestClient) -> None:
    assert _trade(client, "buy", 10).status_code == 201

    response = _trade(client, "sell", 10)

    assert response.status_code == 201
    portfolio = client.get("/api/portfolio").json()
    assert portfolio["positions"] == []
    assert portfolio["cash_balance"] == pytest.approx(STARTING_CASH)
    assert portfolio["total_value"] == pytest.approx(STARTING_CASH)


def test_selling_more_than_held_is_rejected_and_state_unchanged(client: TestClient) -> None:
    assert _trade(client, "buy", 2).status_code == 201
    before = client.get("/api/portfolio").json()

    response = _trade(client, "sell", 3)

    assert response.status_code == 400
    assert "insufficient shares" in response.json()["detail"]
    after = client.get("/api/portfolio").json()
    assert after["cash_balance"] == pytest.approx(before["cash_balance"])
    (position,) = after["positions"]
    assert position["quantity"] == pytest.approx(2.0)