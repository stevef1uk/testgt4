import pytest

from app.ai.structured import parse_trade_intent


def test_parses_buy_intent():
    result = parse_trade_intent("buy 10 AAPL")
    assert result == {"ticker": "AAPL", "side": "buy", "quantity": 10.0}


def test_parses_sell_intent_case_insensitive():
    result = parse_trade_intent("Sell 2.5 nvda")
    assert result == {"ticker": "NVDA", "side": "sell", "quantity": 2.5}


def test_returns_none_for_non_trade_message():
    assert parse_trade_intent("how is my portfolio doing?") is None


@pytest.mark.parametrize("message", ["", "buy AAPL", "buy 0 AAPL", "buy -3 AAPL"])
def test_returns_none_for_invalid_trade(message):
    assert parse_trade_intent(message) is None