from datetime import datetime

from pydantic import ValidationError
import pytest

from app.api.schemas import (
    ChatAction,
    ChatRequest,
    ChatResponse,
    HistoryPoint,
    PortfolioHistory,
    PortfolioPosition,
    PortfolioResponse,
    TradeRequest,
    TradeResponse,
    WatchlistItem,
    WatchlistRequest,
)


def test_market_and_portfolio_contracts_validate_and_dump() -> None:
    watch = WatchlistItem(
        ticker="AAPL",
        price=190.0,
        timestamp=datetime(2024, 1, 1),
        change_direction="up",
    )
    trade = TradeRequest(ticker="AAPL", quantity=2, side="buy")
    position = PortfolioPosition(
        ticker="AAPL",
        quantity=2,
        average_price=180,
        current_price=190,
        market_value=380,
        unrealized_pnl=20,
    )
    portfolio = PortfolioResponse(
        positions=[position], cash=1000, total_value=1380, unrealized_pnl=20
    )

    assert watch.model_dump()["ticker"] == "AAPL"
    assert trade.model_dump() == {"ticker": "AAPL", "quantity": 2.0, "side": "buy"}
    assert portfolio.model_dump()["positions"][0]["market_value"] == 380.0


def test_chat_and_history_contracts_have_safe_empty_collections() -> None:
    history = PortfolioHistory(snapshots=[HistoryPoint(timestamp="2024-01-01", value=100)])
    response = ChatResponse(message="Done", actions=[ChatAction(action="hold")])

    assert history.model_dump()["snapshots"][0]["value"] == 100.0
    assert response.model_dump()["actions"][0]["details"] == {}


def test_requests_reject_blank_values_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        WatchlistRequest(ticker=" ")
    with pytest.raises(ValidationError):
        ChatRequest(message=" ")
    with pytest.raises(ValidationError):
        TradeRequest(ticker="AAPL", quantity=1, side="buy", unexpected=True)

