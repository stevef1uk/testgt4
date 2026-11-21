from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.schemas import (
    ChatAction,
    ChatRequest,
    ChatResponse,
    HistoryPoint,
    PortfolioHistory,
    PortfolioResponse,
    TradeRequest,
    WatchlistRequest,
)


def test_valid_payloads_parse_and_collection_defaults_are_empty() -> None:
    assert WatchlistRequest(ticker="AAPL").ticker == "AAPL"
    assert TradeRequest(ticker="AAPL", quantity=2, side="buy").quantity == 2
    assert PortfolioResponse(cash=1000, total_value=1000, unrealized_pnl=0).positions == []
    assert PortfolioHistory().snapshots == []
    response = ChatResponse(message="done")
    assert response.actions == []
    assert ChatAction(action="buy").details == []
    assert HistoryPoint(timestamp=datetime(2024, 1, 1), value=10).value == 10


@pytest.mark.parametrize(
    "model, payload",
    [
        (WatchlistRequest, {"ticker": " "}),
        (ChatRequest, {"message": "\t"}),
        (TradeRequest, {"ticker": "AAPL", "quantity": 0, "side": "buy"}),
        (TradeRequest, {"ticker": "AAPL", "quantity": 1, "side": "hold"}),
        (TradeRequest, {"ticker": "AAPL", "quantity": -1, "side": "sell"}),
    ],
)
def test_invalid_request_values_are_rejected(model, payload) -> None:
    with pytest.raises(ValidationError):
        model(**payload)


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        WatchlistRequest(ticker="AAPL", unexpected=True)


def test_negative_prices_are_rejected() -> None:
    from app.api.schemas import TradeResponse

    with pytest.raises(ValidationError):
        TradeResponse(
            ticker="AAPL",
            quantity=1,
            side="buy",
            price=-0.01,
            cash=100,
        )