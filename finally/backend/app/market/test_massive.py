from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from app.market.massive import MarketQuote, MassiveProvider


def test_normalize_quote_maps_massive_payload() -> None:
    quote = MassiveProvider.normalize_quote(
        "aapl",
        {"results": {"p": 187.25, "t": 1700000000000}},
    )

    assert quote == MarketQuote(
        ticker="AAPL",
        price=187.25,
        timestamp="1700000000000",
    )


def test_provider_rejects_missing_api_key() -> None:
    import pytest

    with pytest.raises(ValueError, match="api_key must not be empty"):
        MassiveProvider(api_key="")