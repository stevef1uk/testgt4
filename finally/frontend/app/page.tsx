"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import "./polish.css";
import Header from "../components/Header";
import Watchlist from "../components/Watchlist";
import MarketOverview, { MarketOverviewItem } from "../components/MarketOverview";
import PriceChart, { PricePoint } from "../components/PriceChart";
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

interface PriceTickMessage {
  ticker: string;
  price: number;
  previous_price?: number;
  change?: number;
  change_percent?: number;
  change_direction?: string;
  timestamp?: string;
}

function normalisePortfolio(
  raw: unknown,
  priceMap: Record<string, { price: number; change_percent?: number }> = {},
): PortfolioState {
  const data = (raw ?? {}) as Record<string, unknown>;
  const rawPositions = Array.isArray(data.positions)
    ? (data.positions as RawPosition[])
    : [];
  const positions: Position[] = rawPositions.map((p) => {
    const livePrice = priceMap[p.ticker]?.price ?? (Number(p.current_price ?? p.currentPrice) || 0);
    return {
      ticker: p.ticker,
      quantity: Number(p.quantity) || 0,
      avgCost: Number(p.avg_cost ?? p.avgCost) || 0,
      currentPrice: livePrice,
    };
  });
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
  const [prices, setPrices] = useState<Record<string, { price: number; change_percent?: number }>>({});
  const [priceHistory, setPriceHistory] = useState<Record<string, PricePoint[]>>({});

  const loadPortfolio = useCallback(async () => {
    try {
      const res = await fetch("/api/portfolio");
      if (!res.ok) throw new Error(`portfolio ${res.status}`);
      setPortfolio(normalisePortfolio(await res.json(), prices));
    } catch {
      // Don't flip connected here as SSE manages the live feed state
    }
  }, [prices]);

  // Connect to SSE live price stream
  useEffect(() => {
    let es: EventSource | null = null;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      try {
        es = new EventSource("/api/stream/prices");

        es.onopen = () => {
          setConnected(true);
        };

        const handleTick = (tick: PriceTickMessage) => {
          if (!tick || !tick.ticker || typeof tick.price !== "number") return;
          const time = new Date().toLocaleTimeString();

          setPrices((prev) => ({
            ...prev,
            [tick.ticker]: {
              price: tick.price,
              change_percent: tick.change_percent,
            },
          }));

          setPriceHistory((prev) => {
            const history = prev[tick.ticker] || [];
            return {
              ...prev,
              [tick.ticker]: [...history, { time, price: tick.price }].slice(-30),
            };
          });

          setSelectedTicker((current) => current || tick.ticker);
        };

        es.addEventListener("price", (e: MessageEvent) => {
          try {
            const tick = JSON.parse(e.data) as PriceTickMessage;
            handleTick(tick);
          } catch {}
        });

        es.onmessage = (e: MessageEvent) => {
          try {
            const data = JSON.parse(e.data);
            if (Array.isArray(data)) {
              for (const tick of data) {
                handleTick(tick);
              }
            } else if (data && typeof data === "object") {
              handleTick(data as PriceTickMessage);
            }
          } catch {}
        };

        es.onerror = () => {
          setConnected(false);
          es?.close();
          retryTimer = setTimeout(connect, 3000);
        };
      } catch {
        setConnected(false);
        retryTimer = setTimeout(connect, 3000);
      }
    }

    connect();

    return () => {
      if (retryTimer) clearTimeout(retryTimer);
      es?.close();
    };
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

  const marketItems: MarketOverviewItem[] = useMemo(() => {
    const list = Object.entries(prices).map(([ticker, data]) => ({
      ticker,
      price: data.price,
      change_percent: data.change_percent ?? null,
    }));
    return list.sort((a, b) => a.ticker.localeCompare(b.ticker));
  }, [prices]);

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
          <Watchlist prices={prices} onSelect={setSelectedTicker} />
          <MarketOverview items={marketItems} onSelect={setSelectedTicker} />
        </div>
        <div className="flex flex-col gap-4">
          <PriceChart
            ticker={selectedTicker || "AAPL"}
            data={priceHistory[selectedTicker || "AAPL"] || []}
          />
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