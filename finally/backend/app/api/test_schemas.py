"""Unit tests for SPEC Section 8 Pydantic route contracts."""

import pytest
from pydantic import ValidationError

from api.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    PortfolioSnapshot,
    PortfolioSummary,
    TickData,
    TradeRequest,
    TradeResponse,
    WatchlistResponse,
)


def test_tick_data_carries_sse_fields():
    tick = TickData(
        ticker="AAPL",
        price=190.5,
        previous_price=190.0,
        timestamp="2024-01-01T00:00:00Z",
        direction="up",
    )
    assert tick.ticker == "AAPL"
    assert tick.previous_price == 190.0
    assert tick.direction == "up"


def test_tick_data_rejects_invalid_direction():
    with pytest.raises(ValidationError):
        TickData(
            ticker="AAPL",
            price=1.0,
            previous_price=1.0,
            timestamp="t",
            direction="sideways",
        )


def test_trade_request_accepts_buy_and_sell():
    assert TradeRequest(ticker="AAPL", quantity=2, side="buy").side == "buy"
    assert TradeRequest(ticker="AAPL", quantity=2, side="sell").side == "sell"


def test_trade_request_rejects_invalid_side():
    with pytest.raises(ValidationError):
        TradeRequest(ticker="AAPL", quantity=2, side="short")


def test_trade_request_rejects_non_positive_quantity():
    with pytest.raises(ValidationError):
        TradeRequest(ticker="AAPL", quantity=0, side="buy")


def test_trade_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        TradeRequest(ticker="AAPL", quantity=1, side="buy", extra=1)


def test_portfolio_summary_and_snapshot_fields():
    summary = PortfolioSummary(cash_balance=1000.0, total_value=1500.0, unrealized_pnl=500.0)
    snap = PortfolioSnapshot(timestamp="t", total_value=1500.0)
    assert summary.unrealized_pnl == 500.0
    assert snap.total_value == 1500.0


def test_trade_response_fields():
    resp = TradeResponse(
        ticker="AAPL", quantity=1, side="buy", price=190.0, cash_balance=810.0
    )
    assert resp.cash_balance == 810.0


def test_watchlist_response_holds_tickers():
    assert WatchlistResponse(tickers=["AAPL", "MSFT"]).tickers == ["AAPL", "MSFT"]


def test_chat_models_round_trip():
    msg = ChatMessage(role="assistant", content="hi")
    req = ChatRequest(message="buy 1 AAPL")
    resp = ChatResponse(message=msg)
    assert req.message == "buy 1 AAPL"
    assert resp.trades == []
    assert resp.model_dump()["message"]["role"] == "assistant"


def test_chat_message_rejects_invalid_role():
    with pytest.raises(ValidationError):
        ChatMessage(role="system", content="x")
