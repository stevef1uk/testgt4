"""Unit tests for the portfolio engine (buy/sell, positions, valuation)."""

import sqlite3

import pytest

from app.portfolio.engine import InsufficientCashError, InsufficientSharesError, PortfolioEngine
from db.schema import DEFAULT_CASH_BALANCE, DEFAULT_USER_ID, get_db_connection, init_db


@pytest.fixture
def conn(tmp_path):
    init_db(tmp_path / "test.db")
    connection = get_db_connection(tmp_path / "test.db")
    yield connection
    connection.close()


@pytest.fixture
def engine(conn):
    return PortfolioEngine(conn, DEFAULT_USER_ID)


def test_starts_with_default_cash(engine):
    assert engine.cash_balance() == DEFAULT_CASH_BALANCE


def test_buy_reduces_cash_and_creates_position(engine):
    engine.buy("AAPL", 10, 100.0)
    assert engine.cash_balance() == DEFAULT_CASH_BALANCE - 1000.0
    pos = engine.get_position("AAPL")
    assert pos.quantity == 10
    assert pos.avg_cost == 100.0


def test_buy_updates_weighted_average_cost(engine):
    engine.buy("AAPL", 10, 100.0)
    engine.buy("AAPL", 10, 200.0)
    pos = engine.get_position("AAPL")
    assert pos.quantity == 20
    assert pos.avg_cost == pytest.approx(150.0)


def test_buy_rejects_insufficient_cash(engine):
    with pytest.raises(InsufficientCashError):
        engine.buy("AAPL", 1000, 100.0)


def test_sell_reduces_position_and_adds_cash(engine):
    engine.buy("AAPL", 10, 100.0)
    engine.sell("AAPL", 4, 120.0)
    pos = engine.get_position("AAPL")
    assert pos.quantity == 6
    assert engine.cash_balance() == pytest.approx(DEFAULT_CASH_BALANCE - 1000.0 + 480.0)


def test_sell_rejects_more_than_held(engine):
    engine.buy("AAPL", 5, 100.0)
    with pytest.raises(InsufficientSharesError):
        engine.sell("AAPL", 6, 100.0)


def test_selling_all_removes_position(engine):
    engine.buy("AAPL", 5, 100.0)
    engine.sell("AAPL", 5, 100.0)
    assert engine.get_position("AAPL") is None


def test_trades_are_recorded(engine, conn):
    engine.buy("AAPL", 2, 100.0)
    engine.sell("AAPL", 1, 110.0)
    rows = conn.execute(
        "SELECT side, quantity, price FROM trades WHERE user_id = ? ORDER BY id",
        (DEFAULT_USER_ID,),
    ).fetchall()
    assert [tuple(r) for r in rows] == [("buy", 2, 100.0), ("sell", 1, 110.0)]


def test_total_value_uses_current_prices(engine):
    engine.buy("AAPL", 10, 100.0)
    total = engine.total_value({"AAPL": 150.0})
    assert total == pytest.approx(DEFAULT_CASH_BALANCE - 1000.0 + 1500.0)


def test_snapshot_persists_total_value(engine, conn):
    engine.buy("AAPL", 10, 100.0)
    engine.snapshot({"AAPL": 100.0})
    row = conn.execute(
        "SELECT total_value FROM portfolio_snapshots WHERE user_id = ?",
        (DEFAULT_USER_ID,),
    ).fetchone()
    assert row["total_value"] == pytest.approx(DEFAULT_CASH_BALANCE)


def test_execute_trade_dispatches_buy_and_sell(engine):
    engine.execute_trade("AAPL", "buy", 10, 100.0)
    assert engine.get_position("AAPL").quantity == 10
    engine.execute_trade("AAPL", "sell", 4, 100.0)
    assert engine.get_position("AAPL").quantity == 6
    with pytest.raises(Exception):
        engine.execute_trade("AAPL", "hold", 1, 100.0)


def test_get_summary_reports_cash_and_positions(engine):
    engine.buy("AAPL", 3, 100.0)
    summary = engine.get_summary()
    assert summary["cash_balance"] == pytest.approx(DEFAULT_CASH_BALANCE - 300.0)
    assert summary["positions"] == [{"ticker": "AAPL", "quantity": 3, "avg_cost": 100.0}]