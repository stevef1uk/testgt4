"""Integration-level checks for the chat assistant backend modules."""

from app.ai.llm import build_messages, generate_chat_response
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.structured import parse_trade_intent


def test_system_prompt_names_assistant():
    assert "FinAlly, an AI trading assistant" in SYSTEM_PROMPT


def test_trade_message_parses_to_intent():
    assert parse_trade_intent("buy 5 msft") == {
        "ticker": "MSFT",
        "side": "buy",
        "quantity": 5.0,
    }


def test_chat_messages_carry_portfolio_and_user_turn():
    portfolio = {
        "cash_balance": 1000.0,
        "positions": [{"ticker": "AAPL", "quantity": 2, "current_price": 190.0}],
    }
    messages = build_messages("sell 1 AAPL", portfolio, [{"ticker": "NVDA"}])
    assert messages[0]["content"] == SYSTEM_PROMPT
    context = messages[1]["content"]
    assert "1000.00" in context
    assert "AAPL" in context and "NVDA" in context
    assert messages[-1] == {"role": "user", "content": "sell 1 AAPL"}


def test_mock_trade_message_returns_matching_trade():
    messages = [{"role": "user", "content": "buy 5 msft"}]
    result = generate_chat_response(messages, mock=True)
    assert result["trade"] == {"ticker": "MSFT", "side": "buy", "quantity": 5.0}
    assert result["reply"] == "Executed buy 5 MSFT."


def test_mock_non_trade_message_has_no_trade():
    messages = [{"role": "user", "content": "hello there"}]
    result = generate_chat_response(messages, mock=True)
    assert result["trade"] is None
    assert result["reply"] == "You said: hello there"