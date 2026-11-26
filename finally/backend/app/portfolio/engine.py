"""Portfolio valuation and trade execution.

Public API (used by ``app.api.routes_portfolio``):
    get_portfolio_state() -> dict
    get_portfolio_history() -> list[dict]
    execute_trade(payload: dict) -> dict

Persistence is delegated to ``app.portfolio.repository``; that module is
imported lazily so this file compiles before te-9bw lands.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

DEFAULT_CASH = 10_000.0

# Price lookup hook. Default raises for unknown tickers; the market layer can
# replace it via set_price_source() once its interface is wired in.
_price_source: Callable[[str], float | None] = lambda ticker: None


def set_price_source(fn: Callable[[str], float | None]) -> None:
    """Install the function used to look up the current price for a ticker."""
    global _price_source
    _price_source = fn


def _repo() -> Any:
    from app.portfolio import repository  # noqa: PLC0415

    return repository


def _price(ticker: str) -> float:
    price = _price_source(ticker)
    if price is None:
        raise LookupError(f"no price available for {ticker}")
    return float(price)


def get_portfolio_state() -> dict[str, Any]:
    """Return cash, positions with live valuation, and total portfolio value."""
    repo = _repo()
    cash = repo.get_cash_balance(default=DEFAULT_CASH)
    positions = []
    total = cash
    for pos in repo.list_positions():
        price = _price(pos["ticker"])
        market_value = pos["quantity"] * price
        total += market_value
        positions.append(
            {
                "ticker": pos["ticker"],
                "quantity": pos["quantity"],
                "avg_cost": pos["avg_cost"],
                "current_price": price,
                "market_value": market_value,
                "unrealized_pnl": (price - pos["avg_cost"]) * pos["quantity"],
            }
        )
    return {"cash_balance": cash, "total_value": total, "positions": positions}


def get_portfolio_history() -> list[dict[str, Any]]:
    """Return recorded snapshots in chronological order."""
    return _repo().list_snapshots()


def execute_trade(payload: dict[str, Any]) -> dict[str, Any]:
    """Execute a buy or sell at the current price and persist the trade.

    Raises ValueError for invalid input or insufficient cash/shares.
    """
    ticker = str(payload.get("ticker", "")).strip().upper()
    side = payload.get("side")
    quantity = payload.get("quantity")
    if not ticker:
        raise ValueError("ticker is required")
    if side not in ("buy", "sell"):
        raise ValueError("side must be 'buy' or 'sell'")
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        raise ValueError("quantity must be a positive number")

    repo = _repo()
    price = _price(ticker)
    cash = repo.get_cash_balance(default=DEFAULT_CASH)
    held = repo.get_position(ticker)
    held_qty = held["quantity"] if held else 0.0
    cost = quantity * price

    if side == "buy":
        if cost > cash:
            raise ValueError("insufficient cash for buy")
        new_qty = held_qty + quantity
        prior_cost = (held["avg_cost"] * held_qty) if held else 0.0
        avg_cost = (prior_cost + cost) / new_qty
        repo.upsert_position(ticker, new_qty, avg_cost)
        repo.set_cash_balance(cash - cost)
    else:
        if quantity > held_qty:
            raise ValueError("insufficient shares to sell")
        remaining = held_qty - quantity
        if remaining > 0:
            repo.upsert_position(ticker, remaining, held["avg_cost"])
        else:
            repo.delete_position(ticker)
        repo.set_cash_balance(cash + cost)

    trade = repo.record_trade(
        ticker=ticker,
        side=side,
        quantity=float(quantity),
        price=price,
        executed_at=datetime.now(UTC),
    )
    return trade