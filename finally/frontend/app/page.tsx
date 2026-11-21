export default function HomePage() {
  return (
    <main className="page">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Polecat</p>
        <h1 id="page-title">Project workspace</h1>
        <p className="intro">
          A focused workspace for keeping project activity clear, organized, and
          ready for the next step.
        </p>
        <p>$10,000</p>
        <ul aria-label="Tracked tickers">
          {["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "JNJ"].map(
            (ticker) => <li key={ticker}>{ticker}</li>
          )}
        </ul>
      </section>
    </main>
  );
}