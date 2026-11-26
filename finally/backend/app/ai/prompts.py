"""System prompt and market context formatting for the FinAlly chat assistant."""

from __future__ import annotations

from typing import Any

SYSTEM_PROMPT: str = (
    "You are FinAlly, an AI trading assistant. You help the user analyse their "
    "portfolio positions, execute trades in a simulated trading environment, and "
    "manage their watchlist. Be concise, data-driven, and never invent prices. "
    "Always respond with valid structured JSON matching the requested response "
    "schema, with no text outside the JSON object."
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Read a field from a dict or attribute-style object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def format_market_context(portfolio: dict, watchlist: list) -> str:
    """Render cash balance, positions and watchlist tickers as prompt context."""
    portfolio = portfolio or {}
    watchlist = watchlist or []

    cash = _get(portfolio, "cash_balance", _get(portfolio, "cash", 0.0))
    try:
        cash_str = f"{float(cash):.2f}"
    except (TypeError, ValueError):
        cash_str = str(cash)

    lines: list[str] = ["Portfolio context:", f"- Cash balance: ${cash_str}"]

    positions = _get(portfolio, "positions", []) or []
    if positions:
        lines.append("- Positions:")
        for pos in positions:
            ticker = _get(pos, "ticker", "?")
            qty = _get(pos, "quantity", 0)
            price = _get(pos, "current_price", _get(pos, "price"))
            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else "n/a"
            lines.append(f"  - {ticker}: quantity {qty}, price {price_str}")
    else:
        lines.append("- Positions: none")

    tickers: list[str] = []
    for item in watchlist:
        ticker = _get(item, "ticker", item if isinstance(item, str) else None)
        if ticker:
            tickers.append(str(ticker))
    lines.append(
        "- Watchlist tickers: " + (", ".join(tickers) if tickers else "none")
    )

    return "\n".join(lines)