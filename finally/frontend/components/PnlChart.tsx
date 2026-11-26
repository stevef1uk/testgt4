"use client";

import React from "react";

export interface PnlPoint {
  timestamp: string;
  totalValue: number;
}

interface PnlChartProps {
  points: PnlPoint[];
  startingCash?: number;
  width?: number;
  height?: number;
}

const PADDING = 24;

/**
 * Renders portfolio total value over time as an SVG line chart.
 * Plots P&L relative to the starting cash when provided.
 */
export function PnlChart({
  points,
  startingCash,
  width = 480,
  height = 200,
}: PnlChartProps) {
  if (points.length === 0) {
    return (
      <div data-testid="pnl-chart-empty" className="text-sm text-gray-400">
        No portfolio history yet.
      </div>
    );
  }

  const values = points.map((p) =>
    startingCash !== undefined ? p.totalValue - startingCash : p.totalValue,
  );
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 0);
  const span = max - min || 1;

  const innerW = width - PADDING * 2;
  const innerH = height - PADDING * 2;
  const xFor = (i: number) =>
    points.length === 1
      ? PADDING + innerW / 2
      : PADDING + (i / (points.length - 1)) * innerW;
  const yFor = (v: number) => PADDING + (1 - (v - min) / span) * innerH;

  const path = values
    .map((v, i) => `${i === 0 ? "M" : "L"}${xFor(i).toFixed(1)},${yFor(v).toFixed(1)}`)
    .join(" ");

  const last = values[values.length - 1];
  const lineColor = last >= 0 ? "#22c55e" : "#ef4444";

  return (
    <svg
      data-testid="pnl-chart"
      role="img"
      aria-label="Portfolio P&L chart"
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
    >
      <line
        x1={PADDING}
        x2={width - PADDING}
        y1={yFor(0)}
        y2={yFor(0)}
        stroke="#4b5563"
        strokeDasharray="4 4"
      />
      <path d={path} fill="none" stroke={lineColor} strokeWidth={2} />
      <text x={PADDING} y={height - 6} fontSize={10} fill="#9ca3af">
        {points[0].timestamp}
      </text>
      <text
        x={width - PADDING}
        y={height - 6}
        fontSize={10}
        fill="#9ca3af"
        textAnchor="end"
      >
        {points[points.length - 1].timestamp}
      </text>
    </svg>
  );
}

export default PnlChart;