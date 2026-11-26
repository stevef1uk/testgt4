import React, { useState, useEffect } from "react";

export type TradeSide = "buy" | "sell";

export interface TradingPanelProps {
  selectedTicker?: string;
  onTrade?: (side: TradeSide, ticker: string, quantity: number) => void;
}

/**
 * Trading form: ticker + quantity inputs with Buy and Sell buttons.
 * Submits to POST /api/portfolio/trade and reports the outcome in the panel.
 */
export default function TradingPanel({
  selectedTicker = "AAPL",
  onTrade,
}: TradingPanelProps): React.ReactElement {
  const [ticker, setTicker] = useState(selectedTicker);
  const [quantity, setQuantity] = useState("1");
  const [status, setStatus] = useState<string>("");
  const [polishStatus, setPolishStatus] = useState<string>("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (selectedTicker) {
      setTicker(selectedTicker);
    }
  }, [selectedTicker]);

  async function submit(side: TradeSide) {
    const qty = Number(quantity);
    const sym = ticker.trim().toUpperCase();
    if (!sym) {
      setStatus("Enter a ticker");
      setPolishStatus("Enter a ticker");
      return;
    }
    if (!Number.isFinite(qty) || qty <= 0) {
      setStatus("Quantity must be positive");
      setPolishStatus("Enter a positive quantity");
      return;
    }
    setBusy(true);
    setStatus("");
    try {
      const res = await fetch("/api/portfolio/trade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: sym, quantity: qty, side }),
      });
      if (!res.ok) {
        setStatus(`Trade failed (${res.status})`);
        setPolishStatus(`Trade failed`);
      } else {
        setStatus(`${side.toUpperCase()} ${qty} ${sym} filled`);
        setPolishStatus(`${side === "buy" ? "Bought" : "Sold"} ${qty} ${sym}`);
        onTrade?.(side, sym, qty);
      }
    } catch {
      setStatus("Network error");
      setPolishStatus("Network error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section
      aria-label="Trade bar"
      className="p-4 bg-[#161b22] border border-gray-800 rounded-lg space-y-4"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-white">Order Execution</h2>
        <span className="text-xs font-mono text-gray-400">Selected: {ticker}</span>
      </div>

      <form
        data-testid="trading-panel"
        className="trading-panel space-y-3"
        onSubmit={(e) => e.preventDefault()}
      >
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-400">Order Symbol</label>
          <input
            data-testid="trade-ticker"
            aria-label="Order Symbol"
            className="border border-gray-700 bg-gray-900 rounded px-2.5 py-1.5 text-sm text-white font-mono uppercase focus:outline-none focus:border-blue-500"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-400">Quantity</label>
          <input
            data-testid="trade-quantity"
            aria-label="Quantity"
            type="number"
            min="1"
            className="border border-gray-700 bg-gray-900 rounded px-2.5 py-1.5 text-sm text-white font-mono focus:outline-none focus:border-blue-500"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
        </div>

        <div className="flex gap-2 pt-1">
          <button
            type="button"
            data-testid="trade-buy"
            disabled={busy}
            onClick={() => submit("buy")}
            className="flex-1 bg-green-700 hover:bg-green-600 active:bg-green-800 disabled:opacity-50 text-white py-1.5 px-3 rounded font-semibold text-sm transition-colors"
          >
            Buy
          </button>
          <button
            type="button"
            data-testid="trade-sell"
            disabled={busy}
            onClick={() => submit("sell")}
            className="flex-1 bg-red-700 hover:bg-red-600 active:bg-red-800 disabled:opacity-50 text-white py-1.5 px-3 rounded font-semibold text-sm transition-colors"
          >
            Sell
          </button>
        </div>

        {status && (
          <p
            data-testid="trade-status"
            className="text-xs font-medium text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 p-2 rounded"
          >
            {status}
          </p>
        )}
        <p role="status" className="text-xs text-gray-300">
          {polishStatus}
        </p>
      </form>
    </section>
  );
}
