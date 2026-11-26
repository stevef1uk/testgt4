"""Behavioral tests for core market infrastructure: GBM, PriceCache, MassiveClient, SSE."""

import json
import math
import threading
import urllib.parse
from unittest import mock

import pytest

from app.market.cache import PriceCache
from app.market.gbm import TICK_YEAR_FRACTION, GBMDataSimulator
from app.market.massive import MassiveClient
from app.market.sse import format_price_events, format_sse_event


# --- GBMDataSimulator -------------------------------------------------------

def test_gbm_prices_stay_positive_and_finite():
    sim = GBMDataSimulator(seed=1)
    price = 100.0
    for _ in range(1000):
        price = sim.generate_next_price(price, volatility=0.8, drift=0.1)
        assert price > 0
        assert math.isfinite(price)


def test_gbm_fixed_seed_is_deterministic():
    a = GBMDataSimulator(seed=42)
    b = GBMDataSimulator(seed=42)
    seq_a = []
    seq_b = []
    pa = pb = 50.0
    for _ in range(100):
        pa = a.generate_next_price(pa, volatility=0.3, drift=0.05)
        pb = b.generate_next_price(pb, volatility=0.3, drift=0.05)
        seq_a.append(pa)
        seq_b.append(pb)
    assert seq_a == seq_b


def test_gbm_different_seeds_diverge():
    a = GBMDataSimulator(seed=1)
    b = GBMDataSimulator(seed=2)
    assert a.generate_next_price(100.0, 0.5, 0.0) != b.generate_next_price(100.0, 0.5, 0.0)


def test_gbm_zero_volatility_and_zero_drift_keeps_price_constant():
    sim = GBMDataSimulator(seed=7)
    price = 123.45
    for _ in range(50):
        price = sim.generate_next_price(price, volatility=0.0, drift=0.0)
    assert price == 123.45


def test_gbm_zero_volatility_applies_drift_exactly():
    sim = GBMDataSimulator(seed=7)
    result = sim.generate_next_price(100.0, volatility=0.0, drift=0.5)
    assert result == pytest.approx(100.0 * math.exp(0.5 * TICK_YEAR_FRACTION))


# --- PriceCache -------------------------------------------------------------

def test_cache_update_and_get():
    cache = PriceCache()
    assert cache.get("AAPL") is None
    cache.update("AAPL", 190.5)
    assert cache.get("AAPL") == 190.5
    cache.update("AAPL", 191.0)
    assert cache.get("AAPL") == 191.0


def test_cache_snapshot_is_a_copy():
    cache = PriceCache()
    cache.update("AAPL", 10.0)
    snap = cache.snapshot()
    snap["AAPL"] = 999.0
    snap["MSFT"] = 1.0
    assert cache.get("AAPL") == 10.0
    assert cache.get("MSFT") is None

    cache.update("AAPL", 11.0)
    assert snap["AAPL"] == 999.0
    assert cache.snapshot() == {"AAPL": 11.0}


def test_cache_concurrent_updates_are_all_retained():
    cache = PriceCache()
    tickers = [f"T{i}" for i in range(8)]

    def writer(ticker: str) -> None:
        for n in range(200):
            cache.update(ticker, float(n))

    threads = [threading.Thread(target=writer, args=(t,)) for t in tickers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    snap = cache.snapshot()
    assert set(snap) == set(tickers)
    assert all(snap[t] == 199.0 for t in tickers)


# --- MassiveClient ----------------------------------------------------------

def _fake_response(payload: dict) -> mock.MagicMock:
    resp = mock.MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    cm = mock.MagicMock()
    cm.__enter__.return_value = resp
    cm.__exit__.return_value = False
    return cm


def test_massive_parses_last_trade_price():
    client = MassiveClient(api_key="k")
    with mock.patch("app.market.massive.urllib.request.urlopen",
                    return_value=_fake_response({"results": {"p": 191.5}})):
        assert client.get_latest_price("AAPL") == 191.5


def test_massive_builds_url_with_ticker_and_api_key():
    client = MassiveClient(api_key="dummy1", base_url="https://example.test/")  # allow-secret
    with mock.patch("app.market.massive.urllib.request.urlopen",
                    return_value=_fake_response({"results": {"p": 1.0}})) as urlopen:
        client.get_latest_price("MSFT")

    url = urlopen.call_args.args[0]
    parsed = urllib.parse.urlparse(url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "example.test"
    assert parsed.path == "/v2/last/trade/MSFT"
    assert urllib.parse.parse_qs(parsed.query) == {"apiKey": ["dummy1"]}
    assert urlopen.call_args.kwargs["timeout"] == 5.0


def test_massive_returns_float_for_integer_price():
    client = MassiveClient(api_key="k")
    with mock.patch("app.market.massive.urllib.request.urlopen",
                    return_value=_fake_response({"results": {"p": 100}})):
        price = client.get_latest_price("NVDA")
    assert isinstance(price, float)
    assert price == 100.0


# --- SSE formatting ---------------------------------------------------------

def test_sse_frame_has_event_and_data_lines_and_terminator():
    frame = format_sse_event("price", {"ticker": "AAPL", "price": 1.5})
    assert frame == 'event: price\ndata: {"ticker":"AAPL","price":1.5}\n\n'


def test_sse_data_line_round_trips_with_types_preserved():
    payload = {"ticker": "AAPL", "price": 190.25, "direction": "up", "count": 3}
    frame = format_sse_event("price", payload)
    lines = frame.split("\n")
    assert lines[0] == "event: price"
    assert lines[1].startswith("data: ")
    decoded = json.loads(lines[1][len("data: "):])
    assert decoded == payload
    assert isinstance(decoded["price"], float)
    assert isinstance(decoded["count"], int)
    assert isinstance(decoded["ticker"], str)


def test_sse_price_events_preserve_order_and_count():
    ticks = [{"ticker": "AAPL", "price": 1.0}, {"ticker": "MSFT", "price": 2.0}]
    out = format_price_events(ticks)
    assert out.count("event: price\n") == 2
    assert out.index("AAPL") < out.index("MSFT")
    assert out == format_sse_event("price", ticks[0]) + format_sse_event("price", ticks[1])