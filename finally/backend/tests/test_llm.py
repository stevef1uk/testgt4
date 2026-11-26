import json

import pytest

from app.llm import (
    FALLBACK_MESSAGE,
    SYSTEM_PROMPT,
    ChatService,
    LLMError,
    MockLLMClient,
    ParseError,
    build_market_context,
    create_llm_client,
    parse_chat_reply,
)


# --- prompts -----------------------------------------------------------------

def test_context_renders_every_watchlist_ticker_with_live_price():
    prices = {"AAPL": 190.5, "MSFT": 410.0}
    ctx = build_market_context(
        cash=10000.0, positions=[], watchlist=["AAPL", "MSFT"], prices=prices
    )
    assert "AAPL ($190.50)" in ctx
    assert "MSFT ($410.00)" in ctx


def test_context_marks_missing_price_instead_of_dropping_ticker():
    ctx = build_market_context(
        cash=0.0, positions=[], watchlist=["NFLX"], prices={}
    )
    assert "NFLX (price unavailable)" in ctx


def test_system_prompt_requires_json_reply_schema():
    assert "FinAlly" in SYSTEM_PROMPT
    assert '"message"' in SYSTEM_PROMPT
    assert '"trades"' in SYSTEM_PROMPT
    assert '"watchlist_changes"' in SYSTEM_PROMPT


# --- parser ------------------------------------------------------------------

def test_parse_valid_reply_with_trades_and_changes():
    raw = json.dumps(
        {
            "message": "Buying a little AAPL.",
            "trades": [{"ticker": "aapl", "side": "BUY", "quantity": 2}],
            "watchlist_changes": [{"ticker": "nflx", "action": "add"}],
        }
    )
    reply = parse_chat_reply(raw)
    assert reply.message == "Buying a little AAPL."
    assert reply.trades[0].ticker == "AAPL"
    assert reply.trades[0].side == "buy"
    assert reply.trades[0].quantity == 2.0
    assert reply.watchlist_changes[0].ticker == "NFLX"


def test_parse_accepts_fenced_json():
    raw = "```json\n" + json.dumps({"message": "hi"}) + "\n```"
    assert parse_chat_reply(raw).message == "hi"


def test_parse_defaults_missing_lists_to_empty():
    reply = parse_chat_reply(json.dumps({"message": "hello"}))
    assert reply.trades == []
    assert reply.watchlist_changes == []


@pytest.mark.parametrize(
    "raw",
    [
        "not json at all",
        json.dumps(["not", "an", "object"]),
        json.dumps({"trades": []}),
        json.dumps({"message": "x", "trades": [{"ticker": "A", "side": "hold", "quantity": 1}]}),
        json.dumps({"message": "x", "trades": [{"ticker": "A", "side": "buy", "quantity": 0}]}),
        json.dumps({"message": "x", "watchlist_changes": [{"ticker": "A", "action": "poke"}]}),
    ],
)
def test_parse_rejects_schema_violations(raw):
    with pytest.raises(ParseError):
        parse_chat_reply(raw)


# --- client ------------------------------------------------------------------

def test_mock_client_returns_parseable_reply():
    raw = MockLLMClient().complete(SYSTEM_PROMPT, "hello")
    reply = parse_chat_reply(raw)
    assert "hello" in reply.message
    assert reply.trades == []


def test_create_llm_client_uses_mock_when_flag_set(monkeypatch):
    monkeypatch.setenv("LLM_MOCK", "true")
    assert isinstance(create_llm_client(), MockLLMClient)


# --- chat service ------------------------------------------------------------

class _FailingClient:
    def complete(self, system_prompt, user_message):
        raise LLMError("provider down")


class _GarbageClient:
    def complete(self, system_prompt, user_message):
        return "definitely not json"


def test_chat_service_returns_reply_with_context_sent():
    seen = {}

    class _Recording:
        def complete(self, system_prompt, user_message):
            seen["user"] = user_message
            return json.dumps({"message": "ok"})

    service = ChatService(_Recording())
    reply = service.respond(
        user_message="how is AAPL?",
        cash=500.0,
        positions=[],
        watchlist=["AAPL"],
        prices={"AAPL": 190.5},
    )
    assert reply.message == "ok"
    assert "AAPL ($190.50)" in seen["user"]
    assert "how is AAPL?" in seen["user"]


def test_chat_service_falls_back_on_provider_error():
    reply = ChatService(_FailingClient()).respond("hi", 0.0, [], [], {})
    assert reply.message == FALLBACK_MESSAGE
    assert reply.trades == []


def test_chat_service_falls_back_on_malformed_output_without_trades():
    reply = ChatService(_GarbageClient()).respond("hi", 0.0, [], [], {})
    assert reply.message == FALLBACK_MESSAGE
    assert reply.trades == []