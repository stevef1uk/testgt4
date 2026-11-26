"""Unit tests for portfolio valuation, trade execution, and snapshots.

Covers SPEC/plan acceptance for the portfolio engine: buy and sell math,
insufficient cash, oversell rejection, unrealized P&L, and total value.
Each test runs against an isolated in-memory SQLite database.
"""

from __future__ import annotations

import pytest

from app.db.connection import connect
from app.portfolio import engine, repository, snapshots

STARTING_CASH = 10_000.0


@pytest.fixture
def prices() -> dict[str, float]:
    """Mutable price table consumed by the engine's price source."""
    return {"AAPL": 100.0, "MSFT": 50.0}


@pytest.fixture(autouse=True)
def portfolio_env(prices: dict[str, float]):
    """Isolate each test: fresh in-memory DB, known starting cash, injected prices."""
    repository.set_connection(connect(":memory:"))
    repository.set_cash_balance(STARTING_CASH)
    engine.set_price_source(lambda ticker: prices.get(ticker))
    yield
    engine.set_price_source(lambda ticker: None)


# --- Buy math -------------------------------------------------------------


def test_buy_debits_cash_and_creates_position() -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})

    assert repository.get_cash_balance() == pytest.approx(9_000.0)
    position = repository.get_position("AAPL")
    assert position is not None
    assert position["quantity"] == pytest.approx(10.0)
    assert position["avg_cost"] == pytest.approx(100.0)


def test_second_buy_recomputes_weighted_average_cost(prices: dict[str, float]) -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})
    prices["AAPL"] = 200.0
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})

    position = repository.get_position("AAPL")
    assert position is not None
    assert position["quantity"] == pytest.approx(20.0)
    # (10*100 + 10*200) / 20 = 150
    assert position["avg_cost"] == pytest.approx(150.0)
    assert repository.get_cash_balance() == pytest.approx(10_000.0 - 1_000.0 - 2_000.0)


def test_buy_records_trade_with_price_and_quantity() -> None:
    trade = engine.execute_trade({"ticker": "msft", "side": "buy", "quantity": 4})

    assert trade["ticker"] == "MSFT"  # normalised to upper case
    assert trade["side"] == "buy"
    assert trade["quantity"] == pytest.approx(4.0)
    assert trade["price"] == pytest.approx(50.0)
    assert trade["id"] > 0
    assert trade["executed_at"]


# --- Insufficient cash ----------------------------------------------------


def test_buy_with_insufficient_cash_is_rejected_and_state_unchanged() -> None:
    with pytest.raises(ValueError, match="insufficient cash"):
        engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 101})

    assert repository.get_cash_balance() == pytest.approx(STARTING_CASH)
    assert repository.get_position("AAPL") is None
    assert repository.list_snapshots() == []


def test_buy_exactly_available_cash_succeeds() -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 100})

    assert repository.get_cash_balance() == pytest.approx(0.0)


# --- Sell math ------------------------------------------------------------


def test_partial_sell_credits_cash_and_keeps_avg_cost() -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})
    engine.execute_trade({"ticker": "AAPL", "side": "sell", "quantity": 4})

    position = repository.get_position("AAPL")
    assert position is not None
    assert position["quantity"] == pytest.approx(6.0)
    assert position["avg_cost"] == pytest.approx(100.0)
    assert repository.get_cash_balance() == pytest.approx(9_000.0 + 400.0)


def test_full_sell_removes_position() -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 5})
    engine.execute_trade({"ticker": "AAPL", "side": "sell", "quantity": 5})

    assert repository.get_position("AAPL") is None
    assert repository.list_positions() == []
    assert repository.get_cash_balance() == pytest.approx(STARTING_CASH)


# --- Oversell rejection ---------------------------------------------------


def test_sell_more_than_held_is_rejected() -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 3})

    with pytest.raises(ValueError, match="insufficient shares"):
        engine.execute_trade({"ticker": "AAPL", "side": "sell", "quantity": 4})

    position = repository.get_position("AAPL")
    assert position is not None
    assert position["quantity"] == pytest.approx(3.0)


def test_sell_of_unheld_ticker_is_rejected() -> None:
    with pytest.raises(ValueError, match="insufficient shares"):
        engine.execute_trade({"ticker": "MSFT", "side": "sell", "quantity": 1})

    assert repository.get_cash_balance() == pytest.approx(STARTING_CASH)


# --- Input validation -----------------------------------------------------


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"ticker": "", "side": "buy", "quantity": 1}, "ticker is required"),
        ({"ticker": "AAPL", "side": "hold", "quantity": 1}, "side must be"),
        ({"ticker": "AAPL", "side": "buy", "quantity": 0}, "quantity must be a positive"),
        ({"ticker": "AAPL", "side": "buy", "quantity": -2}, "quantity must be a positive"),
        ({"ticker": "AAPL", "side": "buy", "quantity": "3"}, "quantity must be a positive"),
    ],
)
def test_invalid_trade_payloads_are_rejected(payload: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        engine.execute_trade(payload)

    assert repository.list_positions() == []


def test_unknown_price_raises_lookup_error() -> None:
    with pytest.raises(LookupError, match="no price available"):
        engine.execute_trade({"ticker": "ZZZZ", "side": "buy", "quantity": 1})


# --- Valuation and P&L ----------------------------------------------------


def test_portfolio_state_with_no_positions_equals_cash() -> None:
    state = engine.get_portfolio_state()

    assert state["cash_balance"] == pytest.approx(STARTING_CASH)
    assert state["total_value"] == pytest.approx(STARTING_CASH)
    assert state["positions"] == []


def test_unrealized_pnl_and_total_value_track_live_prices(prices: dict[str, float]) -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})  # cost 1000
    prices["AAPL"] = 120.0

    state = engine.get_portfolio_state()
    (position,) = state["positions"]

    assert position["ticker"] == "AAPL"
    assert position["current_price"] == pytest.approx(120.0)
    assert position["market_value"] == pytest.approx(1_200.0)
    assert position["unrealized_pnl"] == pytest.approx(200.0)
    assert state["cash_balance"] == pytest.approx(9_000.0)
    assert state["total_value"] == pytest.approx(9_000.0 + 1_200.0)


def test_unrealized_pnl_is_negative_when_price_falls(prices: dict[str, float]) -> None:
    engine.execute_trade({"ticker": "MSFT", "side": "buy", "quantity": 8})  # cost 400
    prices["MSFT"] = 45.0

    (position,) = engine.get_portfolio_state()["positions"]
    assert position["unrealized_pnl"] == pytest.approx(-40.0)


def test_state_fails_when_held_ticker_has_no_price(prices: dict[str, float]) -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 1})
    del prices["AAPL"]

    with pytest.raises(LookupError):
        engine.get_portfolio_state()


# --- Snapshots and history ------------------------------------------------


def test_snapshot_records_current_total_value(prices: dict[str, float]) -> None:
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})
    result = snapshots.record_portfolio_snapshot()

    assert result["total_value"] == pytest.approx(10_000.0)
    history = engine.get_portfolio_history()
    assert len(history) == 1
    assert history[0]["total_value"] == pytest.approx(10_000.0)
    assert history[0]["recorded_at"]


def test_history_is_chronological_across_snapshots(prices: dict[str, float]) -> None:
    snapshots.record_portfolio_snapshot()
    prices["AAPL"] = 90.0
    engine.execute_trade({"ticker": "AAPL", "side": "buy", "quantity": 10})
    snapshots.record_portfolio_snapshot()

    history = engine.get_portfolio_history()
    assert [h["total_value"] for h in history] == pytest.approx([10_000.0, 10_000.0])
    assert history[0]["recorded_at"] <= history[1]["recorded_at"]