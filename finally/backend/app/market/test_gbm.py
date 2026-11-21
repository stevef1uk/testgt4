from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from app.market.gbm import GBMProvider, generate_prices


def test_generate_prices_is_seeded_positive_and_includes_initial_value() -> None:
    first = generate_prices(initial_price=100.0, count=4, seed=7)
    second = generate_prices(initial_price=100.0, count=4, seed=7)

    assert first == second
    assert len(first) == 5
    assert first[0] == 100.0
    assert all(price > 0 for price in first)


def test_provider_prices_matches_generation_contract() -> None:
    provider = GBMProvider(initial_price=100.0, seed=7)
    assert provider.prices(4) == generate_prices(initial_price=100.0, count=4, seed=7)