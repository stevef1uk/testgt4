"use client";

export interface HeaderProps {
  title?: string;
  totalValue?: number | null;
  cash?: number | null;
  connected?: boolean;
}

function formatUsd(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

export default function Header({
  title = "FinAlly",
  totalValue = null,
  cash = null,
  connected = false,
}: HeaderProps) {
  return (
    <header
      aria-label="Header"
      className="flex items-center justify-between border-b border-gray-700 px-4 py-3"
    >
      <div className="flex items-center gap-3">
        <span className="text-lg font-semibold">{title}</span>
        <span
          data-testid="connection-status"
          data-status={connected ? "connected" : "disconnected"}
          className={`text-xs ${connected ? "text-green-400" : "text-red-400"}`}
        >
          {connected ? "● Live" : "● Offline"}
        </span>
      </div>
      <div className="flex gap-6 font-mono text-sm">
        {totalValue !== null && (
          <span data-testid="total-value">
            <span className="text-gray-400">Total </span>
            {formatUsd(totalValue)}
          </span>
        )}
        {cash !== null && (
          <span data-testid="cash-balance">
            <span className="text-gray-400">Cash </span>
            {formatUsd(cash)}
          </span>
        )}
      </div>
    </header>
  );
}