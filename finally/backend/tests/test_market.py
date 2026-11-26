"""Unit tests for the market data package (base, cache, simulator, massive client, poller, stream)."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import pytest

from app.market.base import PriceTick
from app.market.cache import PriceCache
from app.market.massive_client import MassiveClient, _parse_snapshot
from app.market.poller import PricePoller
from app.market.simulator import SimulatedPriceSource
from app.market.stream import format_sse, price_events, tick_to_dict


def run(coro):
    return asyncio.run(coro)


# --- base -----------------------------------------------------------------

def test_price_tick_rejects_empty_ticker():
    with pytest.raises(ValueError):
        PriceTick(ticker="", price=1.0)


def test_price_tick_rejects_negative_price():
    with pytest.raises(ValueError):
        PriceTick(ticker="AAPL", price=-0.01)


def test_price_tick_default_timestamp_is_timezone_aware_utc():
    tick = PriceTick(ticker="AAPL", price=190.0)
    assert tick.timestamp.tzinfo is not None
    assert tick.timestamp.utcoffset().total_seconds() == 0


def test_price_tick_default_timestamps_are_per_instance():
    first = PriceTick(ticker="AAPL", price=1.0)
    second = PriceTick(ticker="AAPL", price=1.0)
    assert second.timestamp >= first.timestamp
    assert first.timestamp is not second.timestamp


# --- cache ----------------------------------------------------------------

def test_cache_update_and_get_returns_latest_tick():
    async def scenario():
        cache = PriceCache()
        await cache.update(PriceTick(ticker="AAPL", price=190.0))
        await cache.update(PriceTick(ticker="AAPL", price=191.5))
        tick = await cache.get("AAPL")
        assert tick is not None
        assert tick.price == 191.5
        assert len(cache) == 1

    run(scenario())


def test_cache_get_unknown_ticker_returns_none():
    async def scenario():
        assert await PriceCache().get("NOPE") is None

    run(scenario())


def test_cache_get_all_and_remove_and_clear():
    async def scenario():
        cache = PriceCache()
        await cache.update(PriceTick(ticker="AAPL", price=1.0))
        await cache.update(PriceTick(ticker="MSFT", price=2.0))
        tickers = sorted(t.ticker for t in await cache.get_all())
        assert tickers == ["AAPL", "MSFT"]
        await cache.remove("AAPL")
        await cache.remove("MISSING")  # must not raise
        assert [t.ticker for t in await cache.get_all()] == ["MSFT"]
        await cache.clear()
        assert await cache.get_all() == []

    run(scenario())


# --- simulator ------------------------------------------------------------

def test_simulator_rejects_negative_volatility():
    with pytest.raises(ValueError):
        SimulatedPriceSource(volatility=-0.1)


def test_simulator_seeds_start_prices_and_returns_one_tick_per_ticker():
    async def scenario():
        source = SimulatedPriceSource(start_prices={"AAPL": 190.0}, seed=1)
        await source.start(["AAPL", "MSFT", "AAPL"])
        ticks = await source.get_prices()
        assert sorted(t.ticker for t in ticks) == ["AAPL", "MSFT"]
        assert all(t.price > 0 for t in ticks)

    run(scenario())


def test_simulator_is_deterministic_with_seed():
    async def sample():
        source = SimulatedPriceSource(start_prices={"AAPL": 100.0}, seed=42)
        await source.start(["AAPL"])
        return [t.price for t in (await source.get_prices()) + (await source.get_prices())]

    assert run(sample()) == run(sample())


def test_simulator_add_and_remove_ticker():
    async def scenario():
        source = SimulatedPriceSource(seed=3)
        await source.start(["AAPL"])
        await source.add_ticker("TSLA")
        assert {t.ticker for t in await source.get_prices()} == {"AAPL", "TSLA"}
        await source.remove_ticker("AAPL")
        assert {t.ticker for t in await source.get_prices()} == {"TSLA"}

    run(scenario())


# --- massive client -------------------------------------------------------

def test_massive_client_requires_api_key():
    with pytest.raises(ValueError):
        MassiveClient(api_key="")


def test_parse_snapshot_reads_last_trade_price_and_timestamp():
    payload = {
        "tickers": [
            {"ticker": "AAPL", "lastTrade": {"p": 190.25, "t": 1_700_000_000_000_000_000}},
        ]
    }
    ticks = _parse_snapshot(payload)
    assert len(ticks) == 1
    assert ticks[0].ticker == "AAPL"
    assert ticks[0].price == 190.25
    assert ticks[0].timestamp.tzinfo is not None


def test_parse_snapshot_skips_malformed_entries():
    payload = {
        "tickers": [
            {"lastTrade": {"p": 1.0}},  # no symbol
            {"ticker": "MSFT", "lastTrade": {}},  # no price
            {"ticker": "GOOG", "lastTrade": {"p": 150.0}},
        ]
    }
    assert [t.ticker for t in _parse_snapshot(payload)] == ["GOOG"]


def test_parse_snapshot_empty_payload_returns_no_ticks():
    assert _parse_snapshot({}) == []


# --- poller ---------------------------------------------------------------

def test_poller_rejects_non_positive_interval():
    with pytest.raises(ValueError):
        PricePoller(SimulatedPriceSource(), PriceCache(), interval=0)


def test_poller_poll_once_stores_ticks_in_cache():
    async def scenario():
        cache = PriceCache()
        source = SimulatedPriceSource(start_prices={"AAPL": 190.0, "MSFT": 400.0}, seed=7)
        poller = PricePoller(source, cache, interval=0.01)
        await source.start(["AAPL", "MSFT"])
        stored = await poller.poll_once()
        assert stored == 2
        assert (await cache.get("AAPL")) is not None
        assert (await cache.get("MSFT")) is not None

    run(scenario())


def test_poller_start_and_stop_manage_running_state():
    async def scenario():
        cache = PriceCache()
        poller = PricePoller(SimulatedPriceSource(seed=9), cache, interval=0.01)
        await poller.start(["AAPL"])
        assert poller.running
        await asyncio.sleep(0.05)
        await poller.stop()
        assert not poller.running
        assert await cache.get("AAPL") is not None

    run(scenario())


# --- stream ---------------------------------------------------------------

def test_format_sse_emits_event_and_single_data_line():
    frame = format_sse("prices", [{"ticker": "AAPL", "price": 1.0}])
    assert frame.startswith("event: prices\ndata: ")
    assert frame.endswith("\n\n")
    data_line = frame.split("\n")[1]
    assert json.loads(data_line[len("data: "):]) == [{"ticker": "AAPL", "price": 1.0}]


def test_tick_to_dict_serialises_fields():
    ts = datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    assert tick_to_dict(PriceTick(ticker="AAPL", price=12.5, timestamp=ts)) == {
        "ticker": "AAPL",
        "price": 12.5,
        "timestamp": ts.isoformat(),
    }


def test_price_events_yields_snapshot_frame_with_real_prices():
    async def scenario():
        cache = PriceCache()
        await cache.update(PriceTick(ticker="AAPL", price=190.0))
        frames = [f async for f in price_events(cache, interval=0, max_events=1)]
        assert len(frames) == 1
        assert frames[0].startswith("event: prices\n")
        payload = json.loads(frames[0].split("\n")[1][len("data: "):])
        assert payload[0]["ticker"] == "AAPL"
        assert payload[0]["price"] == 190.0

    run(scenario())