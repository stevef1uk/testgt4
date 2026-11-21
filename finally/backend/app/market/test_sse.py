from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from app.market.sse import encode_event, market_event, stream_events


def test_market_event_describes_price_direction() -> None:
    assert market_event("AAPL", 101.0, 100.0, "2024-01-01") == {
        "ticker": "AAPL",
        "price": 101.0,
        "previous_price": 100.0,
        "timestamp": "2024-01-01",
        "change_direction": "up",
    }


def test_encode_event_has_sse_framing_and_optional_metadata() -> None:
    encoded = encode_event({"ticker": "AAPL", "price": 101.0}, event="market", event_id="7")

    assert encoded.startswith("id: 7\nevent: market\ndata: ")
    assert encoded.endswith("\n\n")
    assert '"ticker":"AAPL"' in encoded


def test_stream_events_yields_one_record_per_payload() -> None:
    records = list(stream_events([{"price": 1}, {"price": 2}], event="market"))

    assert len(records) == 2
    assert all(record.startswith("event: market\ndata: ") for record in records)
    assert all(record.endswith("\n\n") for record in records)