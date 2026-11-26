import pytest

from app.ai.prompts import SYSTEM_PROMPT, format_market_context


def test_system_prompt_identifies_assistant():
    assert "FinAlly, an AI trading assistant" in SYSTEM_PROMPT


def test_system_prompt_covers_capabilities_and_json():
    lower = SYSTEM_PROMPT.lower()
    for word in ("analyse", "trade", "watchlist", "json"):
        assert word in lower


def test_market_context_includes_cash_positions_and_watchlist():
    portfolio = {
        "cash_balance": 8500.5,
        "positions": [{"ticker": "AAPL", "quantity": 10, "current_price": 190.25}],
    }
    watchlist = [{"ticker": "MSFT"}, {"ticker": "NVDA"}]
    text = format_market_context(portfolio, watchlist)
    assert "8500.50" in text
    assert "AAPL" in text and "190.25" in text
    assert "MSFT" in text and "NVDA" in text


def test_market_context_handles_empty_state():
    text = format_market_context({"cash_balance": 0}, [])
    assert "Positions: none" in text
    assert "Watchlist tickers: none" in text


@pytest.mark.parametrize("watchlist", [None, []])
def test_market_context_tolerates_missing_watchlist(watchlist):
    assert "Watchlist tickers: none" in format_market_context({}, watchlist)