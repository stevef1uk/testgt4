import React from "react";

export interface HeatmapPosition {
  ticker: string;
  market_value: number;
  unrealized_pnl_percent: number;
}

export interface PortfolioHeatmapProps {
  positions: HeatmapPosition[];
}

/** Map a percent P&L to a background colour: green for gains, red for losses, grey near zero. */
export function heatColor(pnlPercent: number): string {
  if (pnlPercent > 0) return "rgba(34,197,94,0.8)";
  if (pnlPercent < 0) return "rgba(239,68,68,0.8)";
  return "rgba(148,163,184,0.5)";
}

/**
 * Treemap-style heatmap of portfolio positions. Each tile is sized by market
 * value (relative share of the portfolio) and coloured by unrealised P&L %.
 */
export default function PortfolioHeatmap({
  positions,
}: PortfolioHeatmapProps): React.ReactElement {
  const total = positions.reduce((sum, p) => sum + Math.max(p.market_value, 0), 0);

  return (
    <div
      data-testid="portfolio-heatmap"
      className="portfolio-heatmap"
      style={{ display: "flex", flexWrap: "wrap", gap: 4 }}
    >
      {positions.length === 0 && <span>No positions</span>}
      {positions.map((p) => {
        const share = total > 0 ? Math.max(p.market_value, 0) / total : 0;
        return (
          <div
            key={p.ticker}
            data-testid="heatmap-tile"
            data-ticker={p.ticker}
            title={`${p.ticker}: ${p.unrealized_pnl_percent.toFixed(2)}%`}
            style={{
              flexBasis: `${Math.max(share * 100, 8)}%`,
              flexGrow: 1,
              minHeight: 56,
              padding: 8,
              borderRadius: 4,
              background: heatColor(p.unrealized_pnl_percent),
              color: "#fff",
            }}
          >
            <strong>{p.ticker}</strong>
            <div>{p.unrealized_pnl_percent.toFixed(2)}%</div>
          </div>
        );
      })}
    </div>
  );
}