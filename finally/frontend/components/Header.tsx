"use client";

export interface HeaderProps {
  title?: string;
  totalValue?: number | null;
  cash?: number | null;
}

function formatUsd(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

export default function Header({ title = "FinAlly", totalValue = null, cash = null }: HeaderProps) {
  return (
    <header
      aria-label="Header"
      className="flex items-center justify-between border-b border-gray-700 px-4 py-3"
    >
      <span className="text-lg font-semibold">{title}</span>
      <div className="flex gap-6 font-mono text-sm">
        {totalValue !== null && (
          <span>
            <span className="text-gray-400">Total </span>
            {formatUsd(totalValue)}
          </span>
        )}
        {cash !== null && (
          <span>
            <span className="text-gray-400">Cash </span>
            {formatUsd(cash)}
          </span>
        )}
      </div>
    </header>
  );
}