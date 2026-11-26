import React from "react";

export interface PortfolioSnapshot {
  total_value: number;
  recorded_at: string;
}

export interface PnlChartProps {
  snapshots: PortfolioSnapshot[];
  width?: number;
  height?: number;
}

const PADDING = 24;

/**
 * Line chart of total portfolio value over time.
 * Renders one data point per snapshot inside the `pnl-chart` container.
 */
export default function PnlChart({
  snapshots,
  width = 600,
  height = 240,
}: PnlChartProps): React.ReactElement {
  const values = snapshots.map((s) => s.total_value);
  const minV = values.length > 0 ? Math.min(...values) : 0;
  const maxV = values.length > 0 ? Math.max(...values) : 0;
  const span = maxV - minV || 1;
  const innerW = width - PADDING * 2;
  const innerH = height - PADDING * 2;
  const stepX = snapshots.length > 1 ? innerW / (snapshots.length - 1) : 0;

  const points = snapshots.map((s, i) => {
    const x = PADDING + (snapshots.length > 1 ? i * stepX : innerW / 2);
    const y = PADDING + innerH - ((s.total_value - minV) / span) * innerH;
    return { x, y, snapshot: s };
  });

  const polyline = points.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div data-testid="pnl-chart" className="pnl-chart">
      <svg width={width} height={height} role="img" aria-label="Portfolio value over time">
        {points.length > 1 && (
          <polyline
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            points={polyline}
          />
        )}
        {points.map((p, i) => (
          <circle
            key={`${p.snapshot.recorded_at}-${i}`}
            data-testid="pnl-point"
            cx={p.x}
            cy={p.y}
            r={3}
          >
            <title>
              {`${p.snapshot.recorded_at}: ${p.snapshot.total_value}`}
            </title>
          </circle>
        ))}
      </svg>
    </div>
  );
}