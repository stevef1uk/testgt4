const marketData = [
  { ticker: "AAPL", price: "$189.84", change: "+1.24%" },
  { ticker: "MSFT", price: "$421.40", change: "+0.86%" },
  { ticker: "GOOGL", price: "$176.12", change: "+0.51%" },
  { ticker: "AMZN", price: "$186.10", change: "+1.08%" },
  { ticker: "NVDA", price: "$126.09", change: "+2.31%" },
  { ticker: "TSLA", price: "$248.98", change: "-0.42%" },
  { ticker: "META", price: "$567.16", change: "+1.67%" },
  { ticker: "JPM", price: "$211.35", change: "+0.34%" },
  { ticker: "V", price: "$278.46", change: "+0.72%" },
  { ticker: "NFLX", price: "$701.35", change: "+1.92%" },
];

export default function HomePage() {
  return (
    <main className="page">
      <header className="hero" aria-labelledby="page-title">
        <p className="eyebrow">FinAlly</p>
        <h1 id="page-title">Trading dashboard</h1>
        <p className="intro">
          Track your portfolio and follow live market prices in one focused view.
        </p>
      </header>

      <section className="portfolio-card" aria-labelledby="portfolio-title">
        <p className="card-label">Portfolio value</p>
        <h2 id="portfolio-title">$10,000</h2>
        <p className="positive">+$248.40 today · +2.54%</p>
      </section>

      <section className="market-section" aria-labelledby="market-title">
        <div className="section-heading">
          <div>
            <p className="card-label">Market watch</p>
            <h2 id="market-title">Live market prices</h2>
          </div>
          <span className="market-status">Market open</span>
        </div>
        <ul className="ticker-list" aria-label="Tracked tickers">
          {marketData.map(({ ticker, price, change }) => (
            <li className="ticker-row" key={ticker}>
              <span className="ticker-symbol">{ticker}</span>
              <span className="ticker-price">{price}</span>
              <span className={change.startsWith("-") ? "negative" : "positive"}>
                {change}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}