"use client";

import React from "react";

interface PortfolioSummaryProps {
  /** Cash available to trade, in dollars. */
  cash: number;
  /** Sum of market value across all open positions. */
  positionsValue: number;
  /** Cash the portfolio started with, used to compute total P&L. */
  startingCash: number;
}

function money(value: number): string {
  return value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

/**
 * Headline portfolio figures: total value, cash, and P&L against starting cash.
 * Values are driven by live valuation passed in from the parent.
 */
export function PortfolioSummary({
  cash,
  positionsValue,
  startingCash,
}: PortfolioSummaryProps) {
  const totalValue = cash + positionsValue;
  const pnl = totalValue - startingCash;
  const pnlPercent = startingCash > 0 ? (pnl / startingCash) * 100 : 0;
  const pnlClass = pnl >= 0 ? "text-green-400" : "text-red-400";

  return (
    <dl data-testid="portfolio-summary" className="grid grid-cols-2 gap-2 text-sm">
      <dt className="text-gray-400">Total Value</dt>
      <dd data-testid="summary-total-value" className="text-right font-semibold">
        {money(totalValue)}
      </dd>
      <dt className="text-gray-400">Cash</dt>
      <dd data-testid="summary-cash" className="text-right">
        {money(cash)}
      </dd>
      <dt className="text-gray-400">Positions</dt>
      <dd data-testid="summary-positions" className="text-right">
        {money(positionsValue)}
      </dd>
      <dt className="text-gray-400">Total P&amp;L</dt>
      <dd data-testid="summary-pnl" className={`text-right ${pnlClass}`}>
        {money(pnl)} ({pnlPercent.toFixed(2)}%)
      </dd>
    </dl>
  );
}

export default PortfolioSummary;