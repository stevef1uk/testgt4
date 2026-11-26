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
  const [tickerInput, setTickerInput] = useState<string>("");

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
      <form
        className="flex items-center gap-2 px-4 pt-4"
        onSubmit={(e) => {
          e.preventDefault();
          const next = tickerInput.trim().toUpperCase();
          if (next) setSelectedTicker(next);
        }}
      >
        <label htmlFor="ticker-input">Ticker</label>
        <input
          id="ticker-input"
          type="text"
          value={tickerInput}
          onChange={(e) => setTickerInput(e.target.value)}
          placeholder="e.g. AAPL"
          className="rounded border px-2 py-1"
        />
        <button type="submit" className="rounded border px-3 py-1">
          View
        </button>
        <button
          type="button"
          className="rounded border px-3 py-1"
          onClick={() => {
            setTickerInput("");
            setSelectedTicker("");
          }}
        >
          Clear
        </button>
      </form>
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