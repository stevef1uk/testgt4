"""System prompt and live market context construction for the FinAlly chat assistant."""

from collections.abc import Mapping, Sequence
from typing import Any

SYSTEM_PROMPT = """You are FinAlly, an AI trading assistant embedded in a simulated trading workstation.

You help the user understand their portfolio, discuss market conditions using the live prices provided in the context, and execute trades or adjust the watchlist on the user's behalf.

Rules:
- Base every statement about prices and positions on the market context supplied with the request.
- Never invent tickers, prices, or holdings that are not in the context.
- Trades are simulated; only propose trades the user asked for or clearly agreed to.

Response format: respond ONLY with a single JSON object matching this schema, with no prose outside it:
{
  "message": "<string: your reply to the user>",
  "trades": [{"ticker": "<string>", "side": "buy" | "sell", "quantity": <number>}],
  "watchlist_changes": [{"ticker": "<string>", "action": "add" | "remove"}]
}
Use empty arrays when no trades or watchlist changes are needed."""


def format_price(price: float) -> str:
    """Render a price with two decimals and a dollar sign, e.g. ``$190.50``."""
    return f"${price:.2f}"


def _position_line(position: Mapping[str, Any], prices: Mapping[str, float]) -> str:
    ticker = str(position.get("ticker", "?"))
    quantity = position.get("quantity", 0)
    avg_cost = position.get("avg_cost", 0.0)
    live = prices.get(ticker)
    live_text = format_price(live) if live is not None else "price unavailable"
    return (
        f"- {ticker}: {quantity} shares, avg cost {format_price(float(avg_cost))}, "
        f"current {live_text}"
    )


def build_market_context(
    cash: float,
    positions: Sequence[Mapping[str, Any]],
    watchlist: Sequence[str],
    prices: Mapping[str, float],
) -> str:
    """Build the per-request context string from portfolio state and live prices.

    Every watchlist ticker is rendered as ``TICKER ($price)`` using the live
    price from ``prices``; tickers without a cached price are marked as
    unavailable rather than dropped.
    """
    lines: list[str] = [f"Cash balance: {format_price(float(cash))}", "", "Positions:"]
    if positions:
        lines.extend(_position_line(p, prices) for p in positions)
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Watchlist (live prices):")
    if watchlist:
        entries = []
        for ticker in watchlist:
            live = prices.get(ticker)
            price_text = format_price(live) if live is not None else "price unavailable"
            entries.append(f"{ticker} ({price_text})")
        lines.append(", ".join(entries))
    else:
        lines.append("(empty)")

    return "\n".join(lines)


def build_system_messages(
    cash: float,
    positions: Sequence[Mapping[str, Any]],
    watchlist: Sequence[str],
    prices: Mapping[str, float],
) -> str:
    """Return the system prompt followed by the current market context."""
    return f"{SYSTEM_PROMPT}\n\nCurrent market context:\n{build_market_context(cash, positions, watchlist, prices)}"