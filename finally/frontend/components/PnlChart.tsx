"use client";

import { useMemo } from "react";

export interface PnlPoint {
  time: string;
  value: number;
}

export interface PnlChartProps {
  data: PnlPoint[];
  startingValue?: number;
  width?: number;
  height?: number;
}

const PADDING = 8;

export default function PnlChart({
  data,
  startingValue,
  width = 480,
  height = 160,
}: PnlChartProps) {
  const path = useMemo(() => {
    if (data.length < 2) return "";
    const values = data.map((point) => point.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const innerWidth = width - PADDING * 2;
    const innerHeight = height - PADDING * 2;
    return data
      .map((point, index) => {
        const x = PADDING + (index / (data.length - 1)) * innerWidth;
        const y = PADDING + (1 - (point.value - min) / range) * innerHeight;
        return `${index === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(" ");
  }, [data, width, height]);

  const latest = data.length > 0 ? data[data.length - 1].value : null;
  const pnl =
    latest !== null && startingValue !== undefined ? latest - startingValue : null;
  const pnlClass = pnl !== null && pnl < 0 ? "text-red-400" : "text-green-400";

  return (
    <div data-testid="pnl-chart" className="rounded border border-gray-700 p-3">
      <div className="mb-2 flex items-baseline justify-between">
        <span className="font-semibold">Portfolio P&amp;L</span>
        {pnl !== null && (
          <span className={`font-mono text-sm ${pnlClass}`}>
            {pnl >= 0 ? "+" : "-"}${Math.abs(pnl).toFixed(2)}
          </span>
        )}
      </div>
      {path ? (
        <svg
          role="img"
          aria-label="Portfolio P&L chart"
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