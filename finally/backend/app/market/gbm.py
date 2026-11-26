"""Geometric Brownian motion price step for the local market simulator. No database access."""

import math
import random

# One simulation tick expressed as a fraction of a trading year (~0.5 s of a 6.5 h session).
TICK_YEAR_FRACTION = 0.5 / (252 * 6.5 * 3600)


class GBMDataSimulator:
    """Advances a price one tick using the GBM closed-form log-normal step."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def generate_next_price(self, current_price: float, volatility: float, drift: float) -> float:
        z = self._rng.gauss(0.0, 1.0)
        exponent = (drift - 0.5 * volatility**2) * TICK_YEAR_FRACTION
        exponent += volatility * math.sqrt(TICK_YEAR_FRACTION) * z
        return current_price * math.exp(exponent)