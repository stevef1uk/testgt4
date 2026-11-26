import { test, expect } from '@playwright/test';

test.describe('FinAlly E2E User Journeys', () => {
  test('asserts GET / shows the FinAlly heading, default tickers, and cash balance', async ({ page }) => {
    await page.goto('/');

    // Check heading
    const heading = page.locator('header, h1, [aria-label="Header"]').filter({ hasText: 'FinAlly' });
    await expect(heading.first()).toBeVisible();

    // Check starting cash balance of $10,000
    await expect(page.locator('body')).toContainText('10,000');

    // Check that default tickers appear
    const defaultTickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX'];
    for (const ticker of defaultTickers) {
      await expect(page.locator('body')).toContainText(ticker);
    }
  });

  test('covers a market buy and sell round trip', async ({ page, request }) => {
    // Direct API verification of buy and sell flow
    const buyRes = await request.post('/api/portfolio/trades', {
      data: { ticker: 'AAPL', quantity: 2, side: 'buy' },
    });
    expect([200, 201]).toContain(buyRes.status());

    const portfolioRes = await request.get('/api/portfolio');
    expect(portfolioRes.status()).toBe(200);
    const portfolio = await portfolioRes.json();
    expect(portfolio.cash_balance ?? portfolio.cash).toBeLessThan(10000);

    const sellRes = await request.post('/api/portfolio/trades', {
      data: { ticker: 'AAPL', quantity: 1, side: 'sell' },
    });
    expect([200, 201]).toContain(sellRes.status());
  });

  test('covers watchlist add and remove round trip', async ({ request }) => {
    // Add ticker to watchlist
    const addRes = await request.post('/api/watchlist', {
      data: { ticker: 'ORCL' },
    });
    expect([200, 201]).toContain(addRes.status());

    // Check it appears in watchlist
    const listRes = await request.get('/api/watchlist');
    expect(listRes.status()).toBe(200);
    const list = await listRes.json();
    const hasOrcl = list.some((item: { ticker: string }) => item.ticker === 'ORCL');
    expect(hasOrcl).toBe(true);

    // Delete ticker from watchlist
    const delRes = await request.delete('/api/watchlist/ORCL');
    expect([200, 204]).toContain(delRes.status());
  });
});
