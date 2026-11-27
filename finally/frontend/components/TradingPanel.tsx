"use client";

import React, { useState, useEffect } from "react";

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

  useEffect(() => {
    if (defaultTicker) {
      setTicker(defaultTicker);
    }
  }, [defaultTicker]);

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
    <div data-testid="trading-panel" className="panel p-4 space-y-3 text-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 className="font-semibold text-slate-200">Order Execution</h3>
        <span className="text-xs text-slate-400">Market Order • Instant Fill</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Ticker</label>
          <input
            aria-label="Ticker"
            data-testid="trade-ticker"
            placeholder="e.g. AAPL"
            className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 uppercase font-mono text-slate-100 focus:outline-none focus:border-blue-500"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Quantity</label>
          <input
            aria-label="Quantity"
            data-testid="trade-quantity"
            type="number"
            min="1"
            step="any"
            className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-blue-500"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        <span className="text-xs text-slate-500 mr-1">Quick:</span>
        {[1, 5, 10, 50, 100].map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => setQuantity(String(q))}
            className="text-xs px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            {q}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 pt-1">
        <button
          type="button"
          data-testid="trade-buy"
          disabled={submitting}
          onClick={() => submit("buy")}
          className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          Buy {ticker ? ticker.toUpperCase() : ""}
        </button>
        <button
          type="button"
          data-testid="trade-sell"
          disabled={submitting}
          onClick={() => submit("sell")}
          className="w-full py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          Sell {ticker ? ticker.toUpperCase() : ""}
        </button>
      </div>

      {error && (
        <div data-testid="trade-error" role="alert" className="p-2 rounded bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
          {error}
        </div>
      )}
      {status && (
        <div data-testid="trade-status" className="p-2 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs">
          ✓ {status}
        </div>
      )}
    </div>
  );
}

export default TradingPanel;
