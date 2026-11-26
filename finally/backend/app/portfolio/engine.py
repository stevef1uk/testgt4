"""Portfolio engine: cash, positions, trades, valuation, and snapshots."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from db.schema import DEFAULT_USER_ID

_EPS = 1e-9


class PortfolioError(Exception):
    """Base error for portfolio operations."""


class InsufficientCashError(PortfolioError):
    """Raised when a buy costs more than the available cash."""


class InsufficientSharesError(PortfolioError):
    """Raised when a sell exceeds the shares held."""


@dataclass(frozen=True)
class Position:
    ticker: str
    quantity: float
    avg_cost: float


class PortfolioEngine:
    """Executes trades against the SQLite-backed portfolio for one user."""

    def __init__(self, conn: sqlite3.Connection, user_id: str = DEFAULT_USER_ID) -> None:
        self._conn = conn
        self._user_id = user_id

    def cash_balance(self) -> float:
        row = self._conn.execute(
            "SELECT cash_balance FROM users_profile WHERE id = ?",
            (self._user_id,),
        ).fetchone()
        if row is None:
            raise PortfolioError(f"unknown user: {self._user_id}")
        return float(row["cash_balance"])

    def _set_cash(self, amount: float) -> None:
        self._conn.execute(
            "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
            (amount, self._user_id),
        )

    def get_position(self, ticker: str) -> Position | None:
        row = self._conn.execute(
            "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?",
            (self._user_id, ticker),
        ).fetchone()
        if row is None:
            return None
        return Position(
            ticker=row["ticker"],
            quantity=float(row["quantity"]),
            avg_cost=float(row["avg_cost"]),
        )

    def positions(self) -> list[Position]:
        rows = self._conn.execute(
            "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? ORDER BY ticker",
            (self._user_id,),
        ).fetchall()
        return [
            Position(ticker=r["ticker"], quantity=float(r["quantity"]), avg_cost=float(r["avg_cost"]))
            for r in rows
        ]

    def buy(self, ticker: str, quantity: float, price: float) -> None:
        if quantity <= 0 or price <= 0:
            raise PortfolioError("quantity and price must be positive")
        cost = quantity * price
        cash = self.cash_balance()
        if cost > cash + _EPS:
            raise InsufficientCashError(f"need {cost:.2f}, have {cash:.2f}")

        pos = self.get_position(ticker)
        if pos is None:
            new_qty, new_avg = quantity, price
        else:
            new_qty = pos.quantity + quantity
            new_avg = (pos.quantity * pos.avg_cost + cost) / new_qty

        self._conn.execute(
            """
            INSERT INTO positions (user_id, ticker, quantity, avg_cost, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT (user_id, ticker) DO UPDATE SET
                quantity = excluded.quantity,
                avg_cost = excluded.avg_cost,
                updated_at = excluded.updated_at
            """,
            (self._user_id, ticker, new_qty, new_avg),
        )
        self._set_cash(cash - cost)
        self._record_trade(ticker, "buy", quantity, price)
        self._conn.commit()

    def sell(self, ticker: str, quantity: float, price: float) -> None:
        if quantity <= 0 or price <= 0:
            raise PortfolioError("quantity and price must be positive")
        pos = self.get_position(ticker)
        held = pos.quantity if pos else 0.0
        if quantity > held + _EPS:
            raise InsufficientSharesError(f"need {quantity}, hold {held}")

        remaining = held - quantity
        if remaining <= _EPS:
            self._conn.execute(
                "DELETE FROM positions WHERE user_id = ? AND ticker = ?",
                (self._user_id, ticker),
            )
        else:
            self._conn.execute(
                """
                UPDATE positions SET quantity = ?, updated_at = datetime('now')
                WHERE user_id = ? AND ticker = ?
                """,
                (remaining, self._user_id, ticker),
            )
        self._set_cash(self.cash_balance() + quantity * price)
        self._record_trade(ticker, "sell", quantity, price)
        self._conn.commit()

    def _record_trade(self, ticker: str, side: str, quantity: float, price: float) -> None:
        self._conn.execute(
            "INSERT INTO trades (user_id, ticker, side, quantity, price) VALUES (?, ?, ?, ?, ?)",
            (self._user_id, ticker, side, quantity, price),
        )

    def execute_trade(self, ticker: str, side: str, shares: float, price: float) -> None:
        """Dispatch a trade to ``buy`` or ``sell``; rejects unknown sides."""
        if side == "buy":
            self.buy(ticker, shares, price)
        elif side == "sell":
            self.sell(ticker, shares, price)
        else:
            raise PortfolioError(f"invalid side: {side}")

    def get_summary(self) -> dict[str, object]:
        """Return cash balance and open positions for the user."""
        return {
            "cash_balance": self.cash_balance(),
            "positions": [
                {"ticker": p.ticker, "quantity": p.quantity, "avg_cost": p.avg_cost}
                for p in self.positions()
            ],
        }

    def total_value(self, prices: dict[str, float]) -> float:
        """Cash plus market value of positions, using ``prices`` (falls back to avg cost)."""
        total = self.cash_balance()
        for pos in self.positions():
            price = prices.get(pos.ticker, pos.avg_cost)
            total += pos.quantity * price
        return total

    def snapshot(self, prices: dict[str, float]) -> float:
        """Persist the current total value and return it."""
        value = self.total_value(prices)
        self._conn.execute(
            "INSERT INTO portfolio_snapshots (user_id, total_value) VALUES (?, ?)",
            (self._user_id, value),
        )
        self._conn.commit()
        return value