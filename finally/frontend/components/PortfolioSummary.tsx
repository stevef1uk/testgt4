import React from "react";

export interface PortfolioSummaryProps {
  cashBalance: number;
  totalValue: number;
  unrealizedPnl: number;
}

function formatMoney(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

/**
 * Summary bar showing cash balance, total portfolio value and unrealised P&L.
 */
export default function PortfolioSummary({
  cashBalance,
  totalValue,
  unrealizedPnl,
}: PortfolioSummaryProps): React.ReactElement {
  const pnlClass = unrealizedPnl >= 0 ? "pnl-positive" : "pnl-negative";

  return (
    <section data-testid="portfolio-summary" className="portfolio-summary">
      <div>
        <span>Cash</span>
        <strong data-testid="summary-cash">{formatMoney(cashBalance)}</strong>
      </div>
      <div>
        <span>Total Value</span>
        <strong data-testid="summary-total">{formatMoney(totalValue)}</strong>
      </div>
      <div>
        <span>Unrealized P&amp;L</span>
        <strong data-testid="summary-pnl" className={pnlClass}>
          {formatMoney(unrealizedPnl)}
        </strong>
      </div>
    </section>
  );
}