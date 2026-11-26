"use client";

import React from "react";

export interface Position {
  ticker: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
}

interface PositionsTableProps {
  positions: Position[];
}

/**
 * Table of open positions with live valuation. Unrealised P&L is computed
 * from the current price against average cost.
 */
export function PositionsTable({ positions }: PositionsTableProps) {
  if (positions.length === 0) {
    return (
      <div data-testid="positions-empty" className="text-sm text-gray-400">
        No open positions.
      </div>
    );
  }

  return (
    <table data-testid="positions-table" className="w-full text-sm text-left">
      <thead>
        <tr>
          <th className="px-2 py-1">Ticker</th>
          <th className="px-2 py-1 text-right">Qty</th>
          <th className="px-2 py-1 text-right">Avg Cost</th>
          <th className="px-2 py-1 text-right">Price</th>
          <th className="px-2 py-1 text-right">Market Value</th>
          <th className="px-2 py-1 text-right">Unrealised P&amp;L</th>
        </tr>
      </thead>
      <tbody>
        {positions.map((p) => {
          const marketValue = p.quantity * p.currentPrice;
          const pnl = (p.currentPrice - p.avgCost) * p.quantity;
          const pnlClass = pnl >= 0 ? "text-green-400" : "text-red-400";
          return (
            <tr key={p.ticker} data-testid={`position-row-${p.ticker}`}>
              <td className="px-2 py-1 font-semibold">{p.ticker}</td>
              <td className="px-2 py-1 text-right">{p.quantity}</td>
              <td className="px-2 py-1 text-right">{p.avgCost.toFixed(2)}</td>
              <td className="px-2 py-1 text-right">{p.currentPrice.toFixed(2)}</td>
              <td className="px-2 py-1 text-right">{marketValue.toFixed(2)}</td>
              <td className={`px-2 py-1 text-right ${pnlClass}`}>{pnl.toFixed(2)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default PositionsTable;