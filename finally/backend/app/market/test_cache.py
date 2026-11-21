from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from app.market.cache import MarketCache


def test_cache_tracks_latest_previous_and_missing_values() -> None:
    cache = MarketCache()
    first = cache.update("AAPL", 100.0)
    second = cache.update("AAPL", 101.0)

    assert cache.get("AAPL") == second
    assert second.previous_price == first.price
    assert cache.previous("AAPL") == 100.0
    assert cache.get("MSFT") is None


def test_cache_normalizes_naive_timestamp_and_copies_values() -> None:
    cache = MarketCache()
    observed = datetime(2024, 1, 1)
    snapshot = cache.update("MSFT", 200.0, timestamp=observed)

    assert snapshot.timestamp == observed.replace(tzinfo=timezone.utc)
    assert cache.all() == {"MSFT": snapshot}

    cache.clear()
    assert cache.all() == {}


def test_cache_rejects_invalid_inputs() -> None:
    import pytest

    with pytest.raises(ValueError):
        MarketCache().update("", 100.0)
    with pytest.raises(ValueError):
        MarketCache().update("AAPL", -1.0)