"use client";

import { useMemo } from "react";

export interface PricePoint {
  time: string;
  price: number;
}

export interface PriceChartProps {
  ticker: string;
  data: PricePoint[];
  width?: number;
  height?: number;
}

const PADDING = 8;

export default function PriceChart({
  ticker,
  data,
  width = 480,
  height = 160,
}: PriceChartProps) {
  const path = useMemo(() => {
    if (data.length < 2) return "";
    const prices = data.map((point) => point.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;
    const innerWidth = width - PADDING * 2;
    const innerHeight = height - PADDING * 2;
    return data
      .map((point, index) => {
        const x = PADDING + (index / (data.length - 1)) * innerWidth;
        const y = PADDING + (1 - (point.price - min) / range) * innerHeight;
        return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(" ");
  }, [data, width, height]);

  const latest = data.length > 0 ? data[data.length - 1].price : null;

  return (
    <div data-testid="price-chart" className="rounded border border-gray-700 p-3">
      <div className="mb-2 flex items-baseline justify-between">
        <span className="font-semibold">{ticker}</span>
        {latest !== null && (
          <span className="font-mono text-sm">${latest.toFixed(2)}</span>
        )}
      </div>
      {path ? (
        <svg
          role="img"
          aria-label={`${ticker} price chart`}
          viewBox={`0 0 ${width} ${height}`}
          width="100%"
          height={height}
        >
          <path d={path} fill="none" stroke="currentColor" strokeWidth={2} />
        </svg>
      ) : (
        <p className="text-sm text-gray-400">Not enough data to chart.</p>
      )}
    </div>
  );
}