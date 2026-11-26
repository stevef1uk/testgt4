import React from "react";

export interface Position {
  ticker: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
}

export interface PositionsTableProps {
  positions: Position[];
}

function formatMoney(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

/**
 * Table of open positions with quantity, cost basis, current price and unrealised P&L.
 */
export default function PositionsTable({
  positions,
}: PositionsTableProps): React.ReactElement {
  return (
    <table data-testid="positions-table" className="positions-table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Qty</th>
          <th>Avg Cost</th>
          <th>Price</th>
          <th>P&amp;L</th>
          <th>P&amp;L %</th>
        </tr>
      </thead>
      <tbody>
        {positions.length === 0 && (
          <tr>
            <td colSpan={6}>No positions</td>
          </tr>
        )}
        {positions.map((p) => {
          const pnlClass = p.unrealized_pnl >= 0 ? "pnl-positive" : "pnl-negative";
          return (
            <tr key={p.ticker} data-testid="position-row" data-ticker={p.ticker}>
              <td>{p.ticker}</td>
              <td>{p.quantity}</td>
              <td>{formatMoney(p.avg_cost)}</td>
              <td>{formatMoney(p.current_price)}</td>
              <td className={pnlClass}>{formatMoney(p.unrealized_pnl)}</td>
              <td className={pnlClass}>{p.unrealized_pnl_percent.toFixed(2)}%</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}