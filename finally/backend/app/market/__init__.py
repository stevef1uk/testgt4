"""Market data package.

Public surface (resolved lazily so importing the package never pulls in
optional submodules before they exist):

- base:           PriceSource abstract interface and PriceTick model
- simulator:      SimulatedPriceSource (default data source)
- massive_client: MassiveClient (real market data source)
- cache:          PriceCache (latest-price store)
- stream:         SSE price streaming helpers
- poller:         background polling loop feeding the cache
"""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "PriceSource",
    "PriceTick",
    "SimulatedPriceSource",
    "MassiveClient",
    "PriceCache",
    "PricePoller",
]

_EXPORTS: dict[str, str] = {
    "PriceSource": "app.market.base",
    "PriceTick": "app.market.base",
    "SimulatedPriceSource": "app.market.simulator",
    "MassiveClient": "app.market.massive_client",
    "PriceCache": "app.market.cache",
    "PricePoller": "app.market.poller",
}


def __getattr__(name: str) -> Any:
    """Lazily resolve public names from their submodules (PEP 562)."""
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(module_path)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))