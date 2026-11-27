"use client";

import { useEffect, useState, type FormEvent } from "react";

export interface WatchlistItem {
  ticker: string;
}

export interface WatchlistProps {
  apiBase?: string;
  prices?: Record<string, { price: number; change_percent?: number }>;
  onSelect?: (ticker: string) => void;
}

export default function Watchlist({ apiBase = "", prices = {}, onSelect }: WatchlistProps) {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const response = await fetch(`${apiBase}/api/watchlist`);
      if (!response.ok) throw new Error(`Failed to load watchlist (${response.status})`);
      setItems((await response.json()) as WatchlistItem[]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load watchlist");
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiBase]);

  async function handleAdd(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ticker = draft.trim().toUpperCase();
    if (!ticker) return;
    const response = await fetch(`${apiBase}/api/watchlist`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker }),
    });
    if (response.ok) {
      setItems((await response.json()) as WatchlistItem[]);
      setDraft("");
      setError(null);
    } else {
      const body = await response.json().catch(() => ({}));
      setError(typeof body.detail === "string" ? body.detail : `Could not add ${ticker}`);
    }
  }

  async function handleRemove(ticker: string) {
    const response = await fetch(`${apiBase}/api/watchlist/${encodeURIComponent(ticker)}`, {
      method: "DELETE",
    });
    if (response.ok) {
      setItems((await response.json()) as WatchlistItem[]);
      setError(null);
    } else {
      setError(`Could not remove ${ticker}`);
    }
  }

  return (
    <section aria-label="Watchlist" className="flex flex-col gap-2">
      <h2 className="text-sm font-semibold uppercase text-gray-400">Watchlist</h2>
      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          aria-label="Ticker symbol"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Add ticker"
          className="flex-1 rounded bg-gray-800 px-2 py-1 text-sm"
        />
        <button type="submit" className="rounded bg-yellow-600 px-3 py-1 text-sm">
          Add
        </button>
      </form>
      {error && (
        <p role="alert" className="text-sm text-red-400">
          {error}
        </p>
      )}
      <ul className="flex flex-col">
        {items.map((item) => {
          const priceInfo = prices[item.ticker];
          return (
            <li key={item.ticker} className="flex items-center justify-between py-1">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => onSelect?.(item.ticker)}
                  className="font-mono text-sm hover:underline"
                >
                  {item.ticker}
                </button>
                {priceInfo && (
                  <span className="font-mono text-xs text-slate-300">
                    ${priceInfo.price.toFixed(2)}
                  </span>
                )}
              </div>
              <button
                type="button"
                aria-label={`Remove ${item.ticker}`}
                onClick={() => void handleRemove(item.ticker)}
                className="text-xs text-gray-400 hover:text-red-400"
              >
                Remove
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}