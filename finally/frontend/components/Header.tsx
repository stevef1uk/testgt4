"use client";

import { useEffect, useState, useCallback } from "react";
import { getPortfolio, type PortfolioSummary } from "../lib/api";

export type ConnectionStatus = "connected" | "reconnecting" | "disconnected";

const STATUS_DOT_CLASS: Record<ConnectionStatus, string> = {
  connected: "bg-green-500",
  reconnecting: "bg-yellow-400",
  disconnected: "bg-red-500",
};

const STATUS_LABEL: Record<ConnectionStatus, string> = {
  connected: "Connected",
  reconnecting: "Reconnecting",
  disconnected: "Disconnected",
};

export interface HeaderProps {
  title?: string;
  onRefresh?: () => void;
  connectionStatus?: ConnectionStatus;
  cashBalance?: number;
  totalValue?: number;
}

export default function Header({
  title = "FinAlly",
  onRefresh,
  connectionStatus = "connected",
  cashBalance,
  totalValue,
}: HeaderProps) {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      setPortfolio(await getPortfolio());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load portfolio");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleRefresh = () => {
    void load();
    onRefresh?.();
  };

  const cash = cashBalance ?? portfolio?.cash_balance ?? 10000;
  const total = totalValue ?? portfolio?.total_value ?? 10000;
  const formattedCash = cash.toLocaleString("en-US", { style: "currency", currency: "USD" });
  const formattedTotal = total.toLocaleString("en-US", { style: "currency", currency: "USD" });

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-[#0d1117]">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-bold tracking-tight text-white">{title}</h1>
        <span
          data-testid="connection-status"
          aria-label={`Connection status: ${STATUS_LABEL[connectionStatus]}`}
          title={STATUS_LABEL[connectionStatus]}
          className={`inline-block h-3 w-3 rounded-full ${STATUS_DOT_CLASS[connectionStatus]}`}
        />
        <span className="text-xs text-gray-400 hidden sm:inline">{STATUS_LABEL[connectionStatus]}</span>
      </div>
      <div className="flex items-center gap-6 text-sm">
        {error && (
          <span role="alert" className="text-red-400 text-xs">
            {error}
          </span>
        )}
        <div className="flex items-center gap-4">
          <span data-testid="header-total-value" className="text-gray-300 font-medium">
            Total: {formattedTotal}
          </span>
          <span data-testid="header-cash-balance" className="text-gray-200 font-semibold">
            Cash: {formattedCash}
          </span>
          <span data-testid="cash-balance" className="text-gray-400 text-xs">
            Cash: {formattedCash}
          </span>
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium rounded border border-gray-700 transition-colors"
        >
          Refresh
        </button>
      </div>
    </header>
  );
}
