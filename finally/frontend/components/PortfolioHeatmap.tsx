"use client";

import React from "react";

export interface HeatmapPosition {
  ticker: string;
  /** Current market value of the position in dollars. */
  marketValue: number;
  /** Unrealised P&L percentage, e.g. 4.2 for +4.2%. */
  pnlPercent: number;
}

interface PortfolioHeatmapProps {
  positions: HeatmapPosition[];
  width?: number;
  height?: number;
}

const GAP = 2;

function colorFor(pnlPercent: number): string {
  if (pnlPercent > 0) return "#166534";
  if (pnlPercent < 0) return "#991b1b";
  return "#374151";
}

/**
 * Renders positions as a treemap-style grid where tile area is proportional
 * to market value and colour reflects unrealised P&L.
 */
export function PortfolioHeatmap({
  positions,
  width = 480,
  height = 240,
}: PortfolioHeatmapProps) {
  const sorted = positions
    .filter((p) => p.marketValue > 0)
    .sort((a, b) => b.marketValue - a.marketValue);

  if (sorted.length === 0) {
    return (
      <div data-testid="portfolio-heatmap-empty" className="text-sm text-gray-400">
        No positions to display.
      </div>
    );
  }

  const total = sorted.reduce((sum, p) => sum + p.marketValue, 0);
  const cols = Math.ceil(Math.sqrt(sorted.length));
  const rows = Math.ceil(sorted.length / cols);
  const cellW = width / cols;
  const cellH = height / rows;

  return (
    <svg
      data-testid="portfolio-heatmap"
      role="img"
      aria-label="Portfolio heatmap"
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
    >
      {sorted.map((p, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        const x = col * cellW + GAP / 2;
        const y = row * cellH + GAP / 2;
        const w = cellW - GAP;
        const h = cellH - GAP;
        const weight = ((p.marketValue / total) * 100).toFixed(1);
        return (
          <g key={p.ticker} data-testid={`heatmap-tile-${p.ticker}`}>
            <rect x={x} y={y} width={w} height={h} fill={colorFor(p.pnlPercent)} />
            <text x={x + 6} y={y + 16} fontSize={12} fill="#f9fafb">
              {p.ticker}
            </text>
            <text x={x + 6} y={y + 32} fontSize={10} fill="#d1d5db">
              {weight}% · {p.pnlPercent >= 0 ? "+" : ""}
              {p.pnlPercent.toFixed(2)}%
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export default PortfolioHeatmap;