"""Deterministic geometric Brownian motion market provider."""

from __future__ import annotations

import math
import random
from collections.abc import Callable


class GBMProvider:
    """Generate positive prices using a geometric Brownian motion process."""

    def __init__(
        self,
        *,
        initial_price: float = 100.0,
        drift: float = 0.0,
        volatility: float = 0.02,
        seed: int | None = None,
        rng: random.Random | None = None,
    ) -> None:
        if initial_price <= 0:
            raise ValueError("initial_price must be positive")
        if volatility < 0:
            raise ValueError("volatility must be non-negative")
        if seed is not None and rng is not None:
            raise ValueError("seed and rng are mutually exclusive")

        self.initial_price = float(initial_price)
        self.drift = float(drift)
        self.volatility = float(volatility)
        self._rng = rng if rng is not None else random.Random(seed)

    def next_price(self, current_price: float | None = None, dt: float = 1.0) -> float:
        if dt <= 0:
            raise ValueError("dt must be positive")
        price = self.initial_price if current_price is None else float(current_price)
        if price <= 0:
            raise ValueError("current_price must be positive")

        shock = self._rng.gauss(0.0, 1.0)
        exponent = (
            (self.drift - 0.5 * self.volatility**2) * dt
            + self.volatility * math.sqrt(dt) * shock
        )
        return price * math.exp(exponent)

    def prices(self, count: int, dt: float = 1.0) -> list[float]:
        if count < 0:
            raise ValueError("count must be non-negative")

        values = [self.initial_price]
        for _ in range(count):
            values.append(self.next_price(values[-1], dt))
        return values


def generate_prices(
    initial_price: float = 100.0,
    count: int = 1,
    *,
    drift: float = 0.0,
    volatility: float = 0.02,
    seed: int | None = None,
) -> list[float]:
    """Return the initial value followed by ``count`` simulated prices."""
    return GBMProvider(
        initial_price=initial_price,
        drift=drift,
        volatility=volatility,
        seed=seed,
    ).prices(count)