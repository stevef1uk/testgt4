"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type Direction = "up" | "down" | "flat";

type Quote = {
  ticker: string;
  price: number;
  previous: number;
  change: number;
  direction: Direction;
};

type MarketEntry = {
  quote: Quote;
  history: number[];
};

type Position = {
  ticker: string;
  quantity: number;
  averageCost: number;
};

type Trade = {
  id: number;
  side: "buy" | "sell";
  ticker: string;
  quantity: number;
  price: number;
  time: string;
};

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  text: string;
  loading?: boolean;
};

const STARTING_CASH = 10000;
const TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "NFLX"];
const BASE_PRICES: Record<string, number> = {
  AAPL: 189.84,
  MSFT: 421.4,
  GOOGL: 176.12,
  AMZN: 186.1,
  NVDA: 126.09,
  TSLA: 248.98,
  META: 567.16,
  JPM: 211.35,
  V: 278.46,
  NFLX: 701.35,
};

function seedPrice(ticker: string): number {
  if (BASE_PRICES[ticker]) return BASE_PRICES[ticker];
  let hash = 0;
  for (const character of ticker) hash = (hash * 31 + character.charCodeAt(0)) % 10000;
  return 50 + (hash % 350) + (hash % 100) / 100;
}

function money(value: number): string {
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function percent(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function compactMoney(value: number): string {
  return `$${Math.round(value).toLocaleString("en-US")}`;
}

function sparkPoints(values: number[], width: number, height: number): string {
  if (values.length < 2) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / span) * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function Sparkline({ values, direction }: { values: number[]; direction: Direction }) {
  const stroke = direction === "down" ? "#f85149" : direction === "up" ? "#3fb950" : "#8b949e";
  return (
    <svg className="sparkline" viewBox="0 0 90 28" aria-hidden="true">
      <polyline points={sparkPoints(values, 90, 28)} fill="none" stroke={stroke} strokeWidth="1.8" />
    </svg>
  );
}

function PriceChart({ ticker, values }: { ticker: string; values: number[] }) {
  const points = sparkPoints(values, 620, 170);
  const last = values.at(-1) ?? 0;
  return (
    <section className="panel chart-panel" aria-labelledby="chart-title">
      <div className="panel-heading">
        <div>
          <p className="card-label">Selected ticker</p>
          <h2 id="chart-title">{ticker}</h2>
        </div>
        <strong className={values.length > 1 && last < values[0] ? "negative" : "positive"}>{money(last)}</strong>
      </div>
      <svg className="line-chart" viewBox="0 0 620 170" role="img" aria-label={`${ticker} price chart`}>
        <polyline points={points} fill="none" stroke="#58a6ff" strokeWidth="2.5" />
      </svg>
    </section>
  );
}

function PnlChart({ values }: { values: number[] }) {
  return (
    <section className="panel chart-panel" aria-labelledby="pnl-title">
      <div className="panel-heading">
        <div>
          <p className="card-label">Performance</p>
          <h2 id="pnl-title">Portfolio value</h2>
        </div>
        <strong>{money(values.at(-1) ?? STARTING_CASH)}</strong>
      </div>
      <svg className="line-chart" data-testid="pnl-chart" viewBox="0 0 620 170" role="img" aria-label="Portfolio value chart">
        <polyline points={sparkPoints(values, 620, 170)} fill="none" stroke="#d29922" strokeWidth="2.5" />
      </svg>
    </section>
  );
}

function PortfolioHeatmap({ positions, quotes }: { positions: Position[]; quotes: Record<string, Quote> }) {
  const active = positions.filter((position) => position.quantity > 0);
  const totalValue = active.reduce((sum, position) => sum + position.quantity * (quotes[position.ticker]?.price ?? position.averageCost), 0);
  let offset = 0;
  return (
    <section className="panel heatmap-panel" aria-labelledby="heatmap-title">
      <div className="panel-heading">
        <div>
          <p className="card-label">Allocation</p>
          <h2 id="heatmap-title">Portfolio heatmap</h2>
        </div>
      </div>
      <svg className="heatmap" data-testid="portfolio-heatmap" viewBox="0 0 420 120" role="img" aria-label="Portfolio heatmap">
        {active.length === 0 ? (
          <text x="210" y="66" textAnchor="middle" fill="#8b949e">No positions yet</text>
        ) : (
          active.map((position) => {
            const price = quotes[position.ticker]?.price ?? position.averageCost;
            const value = position.quantity * price;
            const width = totalValue ? (value / totalValue) * 420 : 0;
            const pnl = ((price - position.averageCost) / position.averageCost) * 100;
            const x = offset;
            offset += width;
            return (
              <g key={position.ticker}>
                <rect x={x} y="12" width={Math.max(width - 2, 2)} height="96" rx="6" fill={pnl >= 0 ? "#1f6f43" : "#8b1f26"} />
                <text x={x + width / 2} y="50" textAnchor="middle" fill="#f0f6fc" fontSize="12" fontWeight="700">
                  {position.ticker}
                </text>
                <text x={x + width / 2} y="70" textAnchor="middle" fill="#f0f6fc" fontSize="11">
                  {percent(pnl)}
                </text>
              </g>
            );
          })
        )}
      </svg>
    </section>
  );
}

export default function HomePage() {
  const [market, setMarket] = useState<Record<string, MarketEntry>>(() =>
    Object.fromEntries(
      TICKERS.map((ticker) => {
        const price = seedPrice(ticker);
        return [ticker, { quote: { ticker, price, previous: price, change: 0.84, direction: "up" as Direction }, history: [price] }];
      }),
    ),
  );
  const [watchlist, setWatchlist] = useState<string[]>(TICKERS);
  const [selectedTicker, setSelectedTicker] = useState("AAPL");
  const [cash, setCash] = useState(STARTING_CASH);
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [snapshots, setSnapshots] = useState<number[]>([STARTING_CASH]);
  const [chat, setChat] = useState<ChatMessage[]>([
    { id: 0, role: "assistant", text: "Ready. Ask about your portfolio, request a trade, or manage the watchlist." },
  ]);
  const [newTicker, setNewTicker] = useState("");
  const [tradeTicker, setTradeTicker] = useState("AAPL");
  const [quantity, setQuantity] = useState("5");
  const [chatInput, setChatInput] = useState("");
  const [notice, setNotice] = useState("");
  const [connection, setConnection] = useState<"connecting" | "live">("connecting");
  const nextId = useRef(1);

  const quotes = useMemo(
    () => Object.fromEntries(Object.entries(market).map(([ticker, entry]) => [ticker, entry.quote])),
    [market],
  );

  useEffect(() => {
    setConnection("live");
    const timer = window.setInterval(() => {
      setMarket((previous) => {
        const next: Record<string, MarketEntry> = {};
        for (const [ticker, entry] of Object.entries(previous)) {
          const movement = (Math.random() - 0.48) * entry.quote.price * 0.0022;
          const price = Math.max(0.01, entry.quote.price + movement);
          const direction: Direction = price > entry.quote.price ? "up" : price < entry.quote.price ? "down" : "flat";
          next[ticker] = {
            quote: {
              ticker,
              price,
              previous: entry.quote.price,
              change: entry.quote.change + ((price - entry.quote.price) / entry.quote.price) * 100,
              direction,
            },
            history: [...entry.history, price].slice(-48),
          };
        }
        return next;
      });
    }, 850);
    return () => window.clearInterval(timer);
  }, []);

  const portfolioValue = cash + positions.reduce((sum, position) => sum + position.quantity * (quotes[position.ticker]?.price ?? position.averageCost), 0);
  const dayChange = portfolioValue - STARTING_CASH;
  const selectedHistory = market[selectedTicker]?.history ?? [];

  function addTicker(rawTicker: string): { ok: boolean; message: string } {
    const ticker = rawTicker.trim().toUpperCase();
    if (!ticker) return { ok: false, message: "Enter a ticker symbol first." };
    if (watchlist.includes(ticker)) return { ok: false, message: `${ticker} is already in the watchlist.` };
    const price = seedPrice(ticker);
    setMarket((previous) => ({
      ...previous,
      [ticker]: {
        quote: { ticker, price, previous: price, change: 0, direction: "flat" },
        history: [price],
      },
    }));
    setWatchlist((previous) => [...previous, ticker]);
    setSelectedTicker(ticker);
    setNewTicker("");
    return { ok: true, message: `Added ${ticker} to the watchlist.` };
  }

  function removeTicker(ticker: string): { ok: boolean; message: string } {
    if (!watchlist.includes(ticker)) return { ok: false, message: `${ticker} is not in the watchlist.` };
    const remaining = watchlist.filter((item) => item !== ticker);
    setWatchlist(remaining);
    if (selectedTicker === ticker) setSelectedTicker(remaining[0] ?? "");
    return { ok: true, message: `Removed ${ticker} from the watchlist.` };
  }

  function executeTrade(side: "buy" | "sell", ticker: string, rawQuantity: string | number): { ok: boolean; message: string } {
    const symbol = ticker.trim().toUpperCase();
    const amount = Math.floor(Number(rawQuantity));
    const quote = quotes[symbol];
    if (!quote) return { ok: false, message: `${symbol} is not available.` };
    if (!Number.isFinite(amount) || amount <= 0) return { ok: false, message: "Quantity must be a positive whole number." };

    const existing = positions.find((position) => position.ticker === symbol);
    const owned = existing?.quantity ?? 0;
    const notional = amount * quote.price;
    if (side === "buy" && notional > cash) return { ok: false, message: `Insufficient cash for ${amount} ${symbol}.` };
    if (side === "sell" && amount > owned) return { ok: false, message: `Cannot sell ${amount} ${symbol}; you own ${owned}.` };

    const nextPositions = positions
      .map((position) => {
        if (position.ticker !== symbol) return position;
        if (side === "buy") {
          const quantityTotal = position.quantity + amount;
          return {
            ...position,
            quantity: quantityTotal,
            averageCost: (position.averageCost * position.quantity + notional) / quantityTotal,
          };
        }
        return { ...position, quantity: position.quantity - amount };
      })
      .filter((position) => position.quantity > 0);
    if (side === "buy" && !existing) nextPositions.push({ ticker: symbol, quantity: amount, averageCost: quote.price });

    const nextCash = side === "buy" ? cash - notional : cash + notional;
    const nextValue = nextCash + nextPositions.reduce((sum, position) => sum + position.quantity * (quotes[position.ticker]?.price ?? position.averageCost), 0);
    setCash(nextCash);
    setPositions(nextPositions);
    setSnapshots((previous) => [...previous, nextValue].slice(-48));
    setTrades((previous) => [
      {
        id: nextId.current++,
        side,
        ticker: symbol,
        quantity: amount,
        price: quote.price,
        time: new Date().toLocaleTimeString(),
      },
      ...previous,
    ]);
    return { ok: true, message: `${side === "buy" ? "Bought" : "Sold"} ${amount} ${symbol} at ${money(quote.price)}.` };
  }

  function submitTrade(side: "buy" | "sell") {
    const result = executeTrade(side, tradeTicker, quantity);
    setNotice(result.message);
  }

  function submitAddTicker() {
    const result = addTicker(newTicker);
    setNotice(result.message);
  }

  function sendChat() {
    const text = chatInput.trim();
    if (!text) return;
    setChat((previous) => [...previous, { id: nextId.current++, role: "user", text }]);
    setChatInput("");
    const loadingId = nextId.current++;
    setChat((previous) => [...previous, { id: loadingId, role: "assistant", text: "", loading: true }]);

    window.setTimeout(() => {
      let answer = `Your portfolio is worth ${money(portfolioValue)} with ${money(cash)} in cash.`;
      const buyMatch = text.match(/(?:buy|purchase)\s+(\d+)\s+([a-zA-Z.]{1,6})/i) ?? text.match(/(?:buy|purchase)\s+([a-zA-Z.]{1,6})\s+(\d+)/i);
      const sellMatch = text.match(/(?:sell)\s+(\d+)\s+([a-zA-Z.]{1,6})/i) ?? text.match(/(?:sell)\s+([a-zA-Z.]{1,6})\s+(\d+)/i);
      const addMatch = text.match(/(?:add)\s+([a-zA-Z.]{1,6})/i);
      const removeMatch = text.match(/(?:remove|delete)\s+([a-zA-Z.]{1,6})/i);

      if (buyMatch) {
        const first = buyMatch[1];
        const second = buyMatch[2];
        const amount = /^\d+$/.test(first) ? first : second;
        const symbol = /^\d+$/.test(first) ? second : first;
        answer = executeTrade("buy", symbol, amount).message;
      } else if (sellMatch) {
        const first = sellMatch[1];
        const second = sellMatch[2];
        const amount = /^\d+$/.test(first) ? first : second;
        const symbol = /^\d+$/.test(first) ? second : first;
        answer = executeTrade("sell", symbol, amount).message;
      } else if (addMatch) {
        answer = addTicker(addMatch[1]).message;
      } else if (removeMatch) {
        answer = removeTicker(removeMatch[1]).message;
      } else if (/portfolio|value|position|balance/i.test(text)) {
        const positionText = positions.length
          ? positions.map((position) => `${position.quantity} ${position.ticker}`).join(", ")
          : "no open positions";
        answer = `Your portfolio is ${money(portfolioValue)}. Cash is ${money(cash)} and you hold ${positionText}.`;
      }

      setChat((previous) => previous.map((message) => (message.id === loadingId ? { ...message, text: answer, loading: false } : message)));
      setNotice(answer);
    }, 450);
  }

  return (
    <main className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">FinAlly</p>
          <h1 id="page-title">Trading dashboard</h1>
          <p className="intro">Track your portfolio and follow live market prices in one focused view.</p>
        </div>
        <div className="status-cluster">
          <span className="market-status" data-testid="connection-status">
            <span className={`status-dot ${connection}`} /> {connection === "live" ? "Live" : "Connecting"}
          </span>
          <span className="cash-badge">Cash {money(cash)}</span>
        </div>
      </header>

      <section className="portfolio-card" aria-labelledby="portfolio-title">
        <div>
          <p className="card-label">Portfolio value</p>
          <h2 id="portfolio-title">{money(portfolioValue)}</h2>
          <p className={dayChange >= 0 ? "positive" : "negative"}>
            {dayChange >= 0 ? "+" : "-"}{money(Math.abs(dayChange))} today · {percent((dayChange / STARTING_CASH) * 100)}
          </p>
        </div>
        <div className="portfolio-stat">
          <span>Open positions</span>
          <strong>{positions.length}</strong>
        </div>
        <div className="portfolio-stat">
          <span>Trades</span>
          <strong>{trades.length}</strong>
        </div>
      </section>

      {notice ? <p className="notice" role="status">{notice}</p> : null}

      <div className="dashboard-grid">
        <section className="panel watchlist-panel" aria-labelledby="market-title">
          <div className="panel-heading">
            <div>
              <p className="card-label">Market watch</p>
              <h2 id="market-title">Live market prices</h2>
            </div>
          </div>
          <div className="add-row">
            <input
              aria-label="Add ticker"
              placeholder="Add ticker"
              value={newTicker}
              onChange={(event) => setNewTicker(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && submitAddTicker()}
            />
            <button type="button" onClick={submitAddTicker}>Add</button>
          </div>
          <ul className="ticker-list" aria-label="Tracked tickers">
            {watchlist.map((ticker) => {
              const quote = quotes[ticker];
              if (!quote) return null;
              return (
                <li className={`ticker-row ${selectedTicker === ticker ? "selected" : ""}`} key={ticker}>
                  <button className="ticker-select" type="button" onClick={() => setSelectedTicker(ticker)}>
                    <span className="ticker-symbol">{ticker}</span>
                    <Sparkline values={market[ticker].history} direction={quote.direction} />
                    <span className={`ticker-price flash-${quote.direction}`}>{money(quote.price)}</span>
                    <span className={quote.change >= 0 ? "positive" : "negative"}>{percent(quote.change)}</span>
                  </button>
                  <button className="remove-button" type="button" aria-label={`Remove ${ticker}`} onClick={() => setNotice(removeTicker(ticker).message)}>
                    ×
                  </button>
                </li>
              );
            })}
          </ul>
        </section>

        <div className="center-column">
          <PriceChart ticker={selectedTicker} values={selectedHistory} />
          <section className="panel trade-panel" aria-labelledby="trade-title">
            <div className="panel-heading">
              <div>
                <p className="card-label">Orders</p>
                <h2 id="trade-title">Trade</h2>
              </div>
            </div>
            <div className="trade-controls">
              <input aria-label="Trade ticker" placeholder="Ticker" value={tradeTicker} onChange={(event) => setTradeTicker(event.target.value.toUpperCase())} />
              <input aria-label="Quantity" placeholder="Qty" inputMode="numeric" value={quantity} onChange={(event) => setQuantity(event.target.value)} />
              <button type="button" className="buy-button" onClick={() => submitTrade("buy")}>Buy</button>
              <button type="button" className="sell-button" onClick={() => submitTrade("sell")}>Sell</button>
            </div>
          </section>
          <PnlChart values={snapshots} />
        </div>

        <aside className="right-column">
          <section className="panel positions-panel" aria-labelledby="positions-title">
            <div className="panel-heading">
              <div>
                <p className="card-label">Holdings</p>
                <h2 id="positions-title">Positions</h2>
              </div>
            </div>
            {positions.length === 0 ? (
              <p className="empty-state">No positions yet. Buy shares to see them here.</p>
            ) : (
              <table>
                <thead>
                  <tr><th>Symbol</th><th>Qty</th><th>Value</th></tr>
                </thead>
                <tbody>
                  {positions.map((position) => (
                    <tr key={position.ticker}>
                      <td>{position.ticker}</td>
                      <td>{position.quantity}</td>
                      <td>{money(position.quantity * (quotes[position.ticker]?.price ?? position.averageCost))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
          <PortfolioHeatmap positions={positions} quotes={quotes} />
          <section className="panel chat-panel" aria-labelledby="chat-title">
            <div className="panel-heading">
              <div>
                <p className="card-label">Copilot</p>
                <h2 id="chat-title">AI assistant</h2>
              </div>
            </div>
            <div className="chat-history" aria-live="polite">
              {chat.map((message) => (
                <div className={`chat-message ${message.role}`} key={message.id}>
                  {message.loading ? <span className="spinner" aria-label="Loading response" /> : message.text}
                </div>
              ))}
            </div>
            <div className="chat-controls">
              <input
                aria-label="Chat message"
                placeholder="Ask or request a trade"
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && sendChat()}
              />
              <button type="button" className="send-button" onClick={sendChat}>Send</button>
            </div>
          </section>
        </aside>
      </div>
    </main>
  );
}
