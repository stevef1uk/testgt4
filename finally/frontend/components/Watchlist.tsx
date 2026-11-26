"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  addWatchlistTicker,
  getWatchlist,
  removeWatchlistTicker,
  type WatchlistItem,
} from "../lib/api";

export interface WatchlistProps {
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

export default function Watchlist({ selectedTicker, onSelect }: WatchlistProps) {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const load = useCallback(async () => {
    try {
      setError(null);
      const res = await getWatchlist();
      setItems(res.tickers);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load watchlist");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleAdd = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const input = form.elements.namedItem("ticker") as HTMLInputElement | null;
    const ticker = input?.value.trim().toUpperCase() ?? "";
    if (!ticker) return;
    setPending(true);
    setError(null);
    try {
      const res = await addWatchlistTicker(ticker);
      setItems(res.tickers);
      if (input) {
        input.value = "";
      }
      form.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add ticker");
    } finally {
      setPending(false);
    }
  };

  const handleRemove = async (ticker: string) => {
    setPending(true);
    setError(null);
    try {
      const res = await removeWatchlistTicker(ticker);
      setItems(res.tickers);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove ticker");
    } finally {
      setPending(false);
    }
  };

  return (
    <section aria-label="Watchlist" className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-white">Watchlist</h2>
        <span className="text-xs text-gray-400">{items.length} symbols</span>
      </div>

      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          name="ticker"
          type="text"
          placeholder="Add ticker"
          aria-label="Watchlist ticker"
          className="flex-1 bg-gray-950 border border-gray-700 rounded px-2.5 py-1 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={pending}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded text-sm font-medium transition-colors"
        >
          Add
        </button>
      </form>

      {error && (
        <p role="alert" className="text-red-400 text-xs">
          {error}
        </p>
      )}

      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 text-xs border-b border-gray-800">
            <th className="py-1.5 font-medium">Ticker</th>
            <th className="py-1.5 font-medium">Price</th>
            <th className="py-1.5 font-medium">Change</th>
            <th className="py-1.5 text-right font-medium">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const isSelected = selectedTicker === item.ticker;
            return (
              <tr
                key={item.ticker}
                data-testid={`watchlist-row-${item.ticker}`}
                className={`border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors ${
                  isSelected ? "bg-gray-800/70" : ""
                }`}
              >
                <td className="py-2">
                  <button
                    type="button"
                    aria-pressed={isSelected}
                    onClick={() => onSelect?.(item.ticker)}
                    className={`font-semibold hover:text-blue-400 text-left ${
                      isSelected ? "text-blue-400" : "text-gray-200"
                    }`}
                  >
                    {item.ticker}
                  </button>
                </td>
                <td className="py-2 text-gray-300 font-mono">${item.price.toFixed(2)}</td>
                <td
                  className={`py-2 font-mono text-xs ${
                    item.change >= 0 ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {item.change >= 0 ? "+" : ""}
                  {item.change_percent.toFixed(2)}%
                </td>
                <td className="py-2 text-right">
                  <button
                    type="button"
                    onClick={() => void handleRemove(item.ticker)}
                    disabled={pending}
                    aria-label={`Remove ${item.ticker}`}
                    className="px-2 py-0.5 border border-gray-700 hover:border-red-500 text-gray-400 hover:text-red-400 rounded text-xs transition-colors"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
