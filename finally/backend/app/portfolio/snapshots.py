"""Periodic portfolio value snapshot recording."""

from __future__ import annotations

from app.portfolio import engine, repository


def record_portfolio_snapshot() -> dict[str, float]:
    """Compute current total portfolio value and persist it as a snapshot."""
    state = engine.get_portfolio_state()
    total = float(state["total_value"])
    repository.record_snapshot(total)
    return {"total_value": total}