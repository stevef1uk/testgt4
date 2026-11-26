"use client";

import { useEffect, useState } from "react";
import { openPriceStream } from "../lib/sse";

export interface PriceChartProps {
  ticker: string;
  width?: number;
  height?: number;
  maxPoints?: number;
}

export default function PriceChart({
  ticker,
  width = 320,
  height = 120,
  maxPoints = 200,
}: PriceChartProps) {
  const [prices, setPrices] = useState<number[]>([]);

  useEffect(() => {
    setPrices([]);
    const handle = openPriceStream({
      onPrice: (event) => {
        if (event.ticker !== ticker) return;
        setPrices((prev) => {
          const next = [...prev, event.price];
          return next.length > maxPoints ? next.slice(next.length - maxPoints) : next;
        });
      },
    });
    return () => handle.close();
  }, [ticker, maxPoints]);

  const padding = 4;
  const hasData = prices.length > 1;

  let points = "";
  if (hasData) {
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;
    const stepX = (width - padding * 2) / (prices.length - 1);
    points = prices
      .map((p, i) => {
        const x = padding + i * stepX;
        const y = padding + (height - padding * 2) * (1 - (p - min) / range);
        return `${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(" ");
  }

  const last = prices.length > 0 ? prices[prices.length - 1] : null;
  const first = prices.length > 0 ? prices[0] : null;
  const rising = last !== null && first !== null && last >= first;
  const stroke = rising ? "#16a34a" : "#dc2626";

  return (
    <div aria-label={`${ticker} price chart`} className="p-2 space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="font-semibold" data-testid="chart-ticker">
          {ticker}
        </span>
        {last !== null && (
          <span data-testid="chart-last-price">${last.toFixed(2)}</span>
        )}
      </div>
      {hasData ? (
        <svg
          data-testid="chart-svg"
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={`${ticker} trend`}
        >
          <polyline fill="none" stroke={stroke} strokeWidth={2} points={points} />
        </svg>
      ) : (
        <p className="text-sm text-gray-500">Waiting for price data…</p>
      )}
    </div>
  );
}