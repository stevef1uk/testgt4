"use client";

import { useState, useCallback, useEffect } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import MarketOverview from "../components/MarketOverview";
import PriceChart from "../components/PriceChart";
import PortfolioSummary from "../components/PortfolioSummary";
import PortfolioHeatmap from "../components/PortfolioHeatmap";
import PnlChart from "../components/PnlChart";
import PositionsTable, { Position } from "../components/PositionsTable";
import TradingPanel from "../components/TradingPanel";
import ChatAssistant from "../components/ChatAssistant";
import { getPortfolio, PortfolioSummary as ApiPortfolioSummary } from "../lib/api";

export default function Home() {
  const [selectedTicker, setSelectedTicker] = useState<string>("AAPL");
  const [portfolio, setPortfolio] = useState<ApiPortfolioSummary>({
    cash_balance: 10000.0,
    total_value: 10000.0,
    unrealized_pnl: 0.0,
    positions: [],
  });
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const loadPortfolio = useCallback(async () => {
    try {
      const data = await getPortfolio();
      if (data) {
        setPortfolio(data);
      }
    } catch {
      // Use fallback defaults
    }
  }, []);

  useEffect(() => {
    void loadPortfolio();
  }, [loadPortfolio, refreshKey]);

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
    void loadPortfolio();
  };

  const handleTrade = () => {
    handleRefresh();
  };

  // Map API positions to PositionsTable format
  const positions: Position[] = (portfolio.positions || []).map((p) => ({
    ticker: p.ticker,
    quantity: p.quantity,
    avg_cost: p.avg_cost,
    current_price: p.current_price,
    unrealized_pnl: p.unrealized_pnl,
    unrealized_pnl_percent:
      p.avg_cost > 0 ? (p.unrealized_pnl / (p.avg_cost * p.quantity)) * 100 : 0,
  }));

  // Heatmap positions
  const heatmapPositions = positions.map((p) => ({
    ticker: p.ticker,
    market_value: p.quantity * p.current_price,
    unrealized_pnl_percent: p.unrealized_pnl_percent,
  }));

  // P&L snapshots
  const snapshots = [
    { total_value: 10000, recorded_at: "Start" },
    { total_value: portfolio.total_value, recorded_at: "Now" },
  ];

  return (
    <main className="min-h-screen bg-[#0d1117] text-[#e6edf3] flex flex-col font-sans">
      {/* Top Header */}
      <Header
        title="FinAlly"
        connectionStatus="connected"
        cashBalance={portfolio.cash_balance}
        totalValue={portfolio.total_value}
        onRefresh={handleRefresh}
      />

      {/* Main Trading Workstation Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Watchlist */}
        <Sidebar selectedTicker={selectedTicker} onSelect={setSelectedTicker} />

        {/* Center Canvas: Market Overview, Price Chart, Portfolio Analytics */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Market Overview */}
          <MarketOverview refreshKey={refreshKey} />

          {/* Interactive Price Chart for Selected Ticker */}
          <section className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
            <h2 className="text-base font-semibold text-white mb-2">Live Price Chart</h2>
            <PriceChart ticker={selectedTicker} width={640} height={160} />
          </section>

          {/* Portfolio Visualizations */}
          <div className="space-y-4">
            <h2 className="text-base font-semibold text-white">Portfolio Overview</h2>
            <PortfolioSummary
              cashBalance={portfolio.cash_balance}
              totalValue={portfolio.total_value}
              unrealizedPnl={portfolio.unrealized_pnl}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-300 mb-2">Asset Allocation</h3>
                <PortfolioHeatmap positions={heatmapPositions} />
              </div>
              <div className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-300 mb-2">Portfolio Equity Curve</h3>
                <PnlChart snapshots={snapshots} width={380} height={140} />
              </div>
            </div>

            <div className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-300 mb-2">Open Positions</h3>
              <PositionsTable positions={positions} />
            </div>
          </div>
        </div>

        {/* Right Sidebar: Trading Order Entry & AI Chat Assistant */}
        <aside className="w-96 border-l border-gray-800 bg-[#0d1117] p-4 space-y-4 overflow-y-auto shrink-0">
          <TradingPanel selectedTicker={selectedTicker} onTrade={handleTrade} />

          <section aria-label="AI Chat" className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
            <h2 className="text-base font-semibold text-white mb-2">AI Copilot</h2>
            <ChatAssistant />
          </section>
        </aside>
      </div>
    </main>
  );
}
