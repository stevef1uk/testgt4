from app.ai.llm import build_messages
from app.ai.prompts import SYSTEM_PROMPT


def test_build_messages_starts_with_system_prompt():
    messages = build_messages("hello", {"cash_balance": 100.0}, [])
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}


def test_build_messages_includes_context_and_user_message():
    messages = build_messages(
        "buy 1 AAPL", {"cash_balance": 250.0}, [{"ticker": "AAPL"}]
    )
    assert messages[1]["role"] == "system"
    assert "250.00" in messages[1]["content"]
    assert "AAPL" in messages[1]["content"]
    assert messages[-1] == {"role": "user", "content": "buy 1 AAPL"}