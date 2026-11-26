"use client";

import { useState } from "react";
import Header from "../components/Header";
import Watchlist from "../components/Watchlist";
import MarketOverview from "../components/MarketOverview";
import PriceChart from "../components/PriceChart";
import { PortfolioSummary } from "../components/PortfolioSummary";
import { PositionsTable, type Position } from "../components/PositionsTable";
import { TradingPanel } from "../components/TradingPanel";
import ChatAssistant from "../components/ChatAssistant";

const STARTING_CASH = 10000;

export default function Page() {
  const [selectedTicker, setSelectedTicker] = useState<string>("");
  const [cash] = useState<number>(STARTING_CASH);
  const [positions] = useState<Position[]>([]);

  const positionsValue = positions.reduce(
    (sum, p) => sum + p.quantity * p.currentPrice,
    0,
  );
  const totalValue = cash + positionsValue;

  return (
    <div className="flex min-h-screen flex-col">
      <Header
        title="FinAlly"
        totalValue={totalValue}
        cash={cash}
        connected={false}
      />
      <main className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-3">
        <div className="flex flex-col gap-4">
          <Watchlist onSelect={setSelectedTicker} />
          <MarketOverview items={[]} onSelect={setSelectedTicker} />
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
          <TradingPanel defaultTicker={selectedTicker} />
          <ChatAssistant />
        </div>
      </main>
    </div>
  );
}