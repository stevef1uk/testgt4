import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import pytest
from pydantic import ValidationError

from app.api.schemas import TradeRequest, WatchlistItem
from app.market.cache import MarketCache
from app.market.gbm import GBMProvider
from app.market.massive import MassiveProvider
from app.market.sse import encode_event, market_event


def test_schemas_validate_and_serialize_contracts() -> None:
    trade = TradeRequest(ticker="AAPL", quantity=1.5, side="buy")
    item = WatchlistItem(
        ticker="AAPL",
        price=187.25,
        previous_price=186.0,
        timestamp=datetime.now(timezone.utc),
        change_direction="up",
    )

    assert trade.model_dump() == {"ticker": "AAPL", "quantity": 1.5, "side": "buy"}
    assert item.model_dump()["ticker"] == "AAPL"

    with pytest.raises(ValidationError):
        TradeRequest(ticker="AAPL", quantity=0, side="buy")


def test_cache_tracks_latest_previous_and_missing_values() -> None:
    cache = MarketCache()
    first = cache.update("AAPL", 100.0)
    second = cache.update("AAPL", 101.0)

    assert cache.get("AAPL") == second
    assert second.previous_price == first.price
    assert cache.previous("AAPL") == 100.0
    assert cache.get("MSFT") is None


def test_massive_normalizes_mocked_payload_without_network() -> None:
    quote = MassiveProvider.normalize_quote(
        "aapl",
        {"results": {"p": 187.25, "t": 1700000000000}},
    )

    assert quote.ticker == "AAPL"
    assert quote.price == 187.25
    assert quote.timestamp == "1700000000000"


def test_gbm_is_seeded_positive_and_has_requested_shape() -> None:
    first = GBMProvider(initial_price=100.0, seed=7).prices(4)
    second = GBMProvider(initial_price=100.0, seed=7).prices(4)

    assert first == second
    assert len(first) == 5
    assert first[0] == 100.0
    assert all(price > 0 for price in first)


def test_sse_event_has_required_fields_and_data_framing() -> None:
    payload = market_event("AAPL", 101.0, 100.0, "2024-01-01T00:00:00Z")
    encoded = encode_event(payload)
    decoded = json.loads(encoded.removeprefix("data: ").rstrip("\n"))

    assert encoded.startswith("data: ")
    assert encoded.endswith("\n\n")
    assert decoded == payload
    assert decoded["change_direction"] == "up"