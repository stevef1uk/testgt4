"use client";

import { useCallback, useEffect, useState } from "react";
import { getWatchlist, type WatchlistItem } from "../lib/api";
import { openPriceStream, type PriceEvent } from "../lib/sse";

export interface MarketOverviewProps {
  refreshKey?: number;
}

export default function MarketOverview({ refreshKey = 0 }: MarketOverviewProps) {
  const [tickers, setTickers] = useState<WatchlistItem[]>([]);
  const [prices, setPrices] = useState<Record<string, PriceEvent>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setError(null);
      const res = await getWatchlist();
      setTickers(res.tickers);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load market overview");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  useEffect(() => {
    const handle = openPriceStream({
      onPrice: (event) => {
        setPrices((prev) => ({ ...prev, [event.ticker]: event }));
      },
    });
    return () => handle.close();
  }, []);

  return (
    <section aria-label="Market overview" className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Market Overview</h2>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="px-2 py-1 border rounded text-sm"
        >
          {loading ? "Loading…" : "Reload"}
        </button>
      </div>

      {error && (
        <p role="alert" className="text-red-600 text-sm">
          {error}
        </p>
      )}

      <ul className="grid grid-cols-2 gap-2">
        {tickers.map((item) => {
          const live = prices[item.ticker];
          const price = live?.price ?? item.price;
          const change = live?.change ?? item.change;
          const changePct = live?.change_percent ?? item.change_percent;
          const up = change >= 0;
          return (
            <li
              key={item.ticker}
              data-testid={`market-card-${item.ticker}`}
              className="border rounded p-2 text-sm"
            >
              <div className="font-semibold">{item.ticker}</div>
              <div data-testid={`market-price-${item.ticker}`}>${price.toFixed(2)}</div>
              <div className={up ? "text-green-600" : "text-red-600"}>
                {changePct.toFixed(2)}%
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}