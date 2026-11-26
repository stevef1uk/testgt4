"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import "./polish.css";
import Header from "../components/Header";
import Watchlist from "../components/Watchlist";
import MarketOverview from "../components/MarketOverview";
import PriceChart from "../components/PriceChart";
import { PortfolioSummary } from "../components/PortfolioSummary";
import { PositionsTable, type Position } from "../components/PositionsTable";
import { TradingPanel } from "../components/TradingPanel";
import ChatAssistant from "../components/ChatAssistant";

const STARTING_CASH = 10000;
const POLL_MS = 5000;

interface RawPosition {
  ticker: string;
  quantity: number;
  avg_cost?: number;
  avgCost?: number;
  current_price?: number;
  currentPrice?: number;
}

interface PortfolioState {
  cash: number;
  positions: Position[];
}

function normalisePortfolio(raw: unknown): PortfolioState {
  const data = (raw ?? {}) as Record<string, unknown>;
  const rawPositions = Array.isArray(data.positions)
    ? (data.positions as RawPosition[])
    : [];
  const positions: Position[] = rawPositions.map((p) => ({
    ticker: p.ticker,
    quantity: Number(p.quantity) || 0,
    avgCost: Number(p.avg_cost ?? p.avgCost) || 0,
    currentPrice: Number(p.current_price ?? p.currentPrice) || 0,
  }));
  const cash = Number(data.cash ?? data.cash_balance ?? STARTING_CASH);
  return { cash: Number.isFinite(cash) ? cash : STARTING_CASH, positions };
}

export default function Page() {
  const [selectedTicker, setSelectedTicker] = useState<string>("");
  const [portfolio, setPortfolio] = useState<PortfolioState>({
    cash: STARTING_CASH,
    positions: [],
  });
  const [connected, setConnected] = useState<boolean>(false);

  const loadPortfolio = useCallback(async () => {
    try {
      const res = await fetch("/api/portfolio");
      if (!res.ok) throw new Error(`portfolio ${res.status}`);
      setPortfolio(normalisePortfolio(await res.json()));
      setConnected(true);
    } catch {
      setConnected(false);
    }
  }, []);

  useEffect(() => {
    void loadPortfolio();
    const id = setInterval(() => void loadPortfolio(), POLL_MS);
    return () => clearInterval(id);
  }, [loadPortfolio]);

  const { cash, positions } = portfolio;
  const positionsValue = useMemo(
    () => positions.reduce((sum, p) => sum + p.quantity * p.currentPrice, 0),
    [positions],
  );
  const totalValue = cash + positionsValue;

  const marketItems = useMemo(
    () =>
      positions.map((p) => ({ ticker: p.ticker, price: p.currentPrice })),
    [positions],
  );

  async function sendChat(message: string): Promise<string> {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) return `Request failed (${res.status}).`;
    const data = (await res.json()) as { message?: string };
    void loadPortfolio();
    return data.message ?? "";
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header
        title="FinAlly"
        totalValue={totalValue}
        cash={cash}
        connected={connected}
      />
      <div className="flex items-center justify-end gap-2 px-4 pt-4">
        <button
          type="button"
          onClick={() => void loadPortfolio()}
          className="rounded border border-slate-700 px-3 py-1 text-sm hover:bg-slate-800"
        >
          Refresh portfolio
        </button>
      </div>
      <main className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-3">
        <div className="flex flex-col gap-4">
          <Watchlist onSelect={setSelectedTicker} />
          <MarketOverview items={marketItems} onSelect={setSelectedTicker} />
        </div>
        <div className="flex flex-col gap-4">
          <PriceChart ticker={selectedTicker} data={[]} />
          <PortfolioSummary
            cash={cash}
            positionsValue={positionsValue}
            startingCash={STARTING_CASH}
          />
          <PositionsTable positions={positions} />
        </div>
        <div className="flex flex-col gap-4">
          <TradingPanel
            defaultTicker={selectedTicker}
            onTraded={() => void loadPortfolio()}
          />
          <ChatAssistant onSend={sendChat} />
        </div>
      </main>
    </div>
  );
}