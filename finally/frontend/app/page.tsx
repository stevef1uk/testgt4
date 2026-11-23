export const metadata = {
  title: 'FinAlly Dashboard',
  description: 'AI Trading Workstation - Portfolio and Market Overview',
}

export default function DashboardPage() {
  return (
    <main className='min-h-screen bg-gray-900 text-white p-6'>
      <h1 className='text-3xl font-bold mb-6'>FinAlly Trading Workstation</h1>
      <section className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        <div className='bg-gray-800 rounded-lg p-4 border border-gray-700'>
          <h2 className='text-lg font-semibold mb-4'>Watchlist</h2>
          <div className='space-y-2' id='watchlist-container'>
            {['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX'].map((ticker) => (
              <div key={ticker} className='text-sm' id={`ticker-${ticker}`}>
                {ticker}
              </div>
            ))}
          </div>
        </div>
        <div className='bg-gray-800 rounded-lg p-4 border border-gray-700 md:col-span-2'>
          <h2 className='text-lg font-semibold mb-4'>Price Chart</h2>
          <div id='chart-container' className='h-64 bg-gray-900 rounded border border-gray-700' />
        </div>
      </section>
      <section className='mt-8 bg-gray-800 rounded-lg p-4 border border-gray-700'>
        <h2 className='text-lg font-semibold mb-4'>Portfolio</h2>
        <div id='portfolio-summary'>$10,000</div>
      </section>
    </main>
  )
}