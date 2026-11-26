"use client";

import React, { useState } from "react";

export type TradeSide = "buy" | "sell";

interface TradingPanelProps {
  /** Ticker pre-filled in the form, e.g. from the watchlist selection. */
  defaultTicker?: string;
  /** Called after a trade is accepted by the backend. */
  onTraded?: () => void;
}

/**
 * Buy/sell order form. Submits to POST /api/portfolio/trades and reports
 * the backend's rejection message (e.g. selling more than held) inline.
 */
export function TradingPanel({ defaultTicker = "", onTraded }: TradingPanelProps) {
  const [ticker, setTicker] = useState(defaultTicker);
  const [quantity, setQuantity] = useState("1");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(side: TradeSide) {
    setStatus(null);
    setError(null);
    const qty = Number(quantity);
    if (!ticker.trim()) {
      setError("Enter a ticker.");
      return;
    }
    if (!Number.isFinite(qty) || qty <= 0) {
      setError("Quantity must be a positive number.");
      return;
    }
    setSubmitting(true);
    try {
      const res = await fetch("/api/portfolio/trades", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker: ticker.trim().toUpperCase(),
          side,
          quantity: qty,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setError(typeof body.detail === "string" ? body.detail : `Trade failed (${res.status})`);
        return;
      }
      setStatus(`${side === "buy" ? "Bought" : "Sold"} ${qty} ${ticker.trim().toUpperCase()}`);
      onTraded?.();
    } catch {
      setError("Network error submitting trade.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div data-testid="trading-panel" className="space-y-2 text-sm">
      <div className="flex gap-2">
        <input
          aria-label="Ticker"
          data-testid="trade-ticker"
          className="bg-transparent border px-2 py-1 w-24 uppercase"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
        <input
          aria-label="Quantity"
          data-testid="trade-quantity"
          type="number"
          min="0"
          step="any"
          className="bg-transparent border px-2 py-1 w-24"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          data-testid="trade-buy"
          disabled={submitting}
          onClick={() => submit("buy")}
          className="px-3 py-1 bg-green-700 text-white disabled:opacity-50"
        >
          Buy
        </button>
        <button
          type="button"
          data-testid="trade-sell"
          disabled={submitting}
          onClick={() => submit("sell")}
          className="px-3 py-1 bg-red-700 text-white disabled:opacity-50"
        >
          Sell
        </button>
      </div>
      {error && (
        <p data-testid="trade-error" role="alert" className="text-red-400">
          {error}
        </p>
      )}
      {status && (
        <p data-testid="trade-status" className="text-green-400">
          {status}
        </p>
      )}
    </div>
  );
}

export default TradingPanel;