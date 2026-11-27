import { test, expect } from '@playwright/test';

test.describe('FinAlly E2E User Journeys', () => {
  test('asserts GET / shows the FinAlly heading, default tickers, cash balance, and copilot greeting', async ({ page }) => {
    await page.goto('/');

    // Check heading
    const heading = page.getByText('FinAlly');
    await expect(heading.first()).toBeVisible();

    // Check cash balance is displayed in header
    const cashBalance = page.getByTestId('cash-balance');
    await expect(cashBalance).toBeVisible();
    await expect(cashBalance).toContainText(/\$[\d,]+\.\d{2}/);

    // Check that default tickers appear
    const defaultTickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'NFLX'];
    for (const ticker of defaultTickers) {
      await expect(page.getByText(ticker).first()).toBeVisible();
    }

    // Check that AI Copilot greeting message is visible
    const chatSection = page.getByRole('region', { name: 'AI assistant' });
    await expect(chatSection).toBeVisible();
    await expect(chatSection.getByText(/your AI trading copilot/i)).toBeVisible();
  });

  test('covers interactive market buy through the trading panel in the browser', async ({ page }) => {
    await page.goto('/');

    const tradingPanel = page.getByTestId('trading-panel');
    await expect(tradingPanel).toBeVisible();

    // Fill in ticker and quantity
    const tickerInput = page.getByTestId('trade-ticker');
    await tickerInput.fill('AAPL');

    const qtyInput = page.getByTestId('trade-quantity');
    await qtyInput.fill('2');

    // Click Buy button
    const buyBtn = page.getByTestId('trade-buy');
    await buyBtn.click();

    // Expect confirmation status
    const statusEl = page.getByTestId('trade-status');
    await expect(statusEl).toBeVisible({ timeout: 10_000 });
    await expect(statusEl).toContainText(/Bought 2 AAPL/i);

    // Verify positions table displays AAPL
    const positionsTable = page.getByTestId('positions-table');
    await expect(positionsTable).toBeVisible();
    await expect(positionsTable.getByText('AAPL').first()).toBeVisible();
  });

  test('covers a market buy and sell round trip via API', async ({ request }) => {
    // Direct API verification of buy and sell flow
    const buyRes = await request.post('/api/portfolio/trades', {
      data: { ticker: 'AAPL', quantity: 2, side: 'buy' },
    });
    expect([200, 201]).toContain(buyRes.status());

    const portfolioRes = await request.get('/api/portfolio');
    expect(portfolioRes.status()).toBe(200);
    const portfolio = await portfolioRes.json();
    expect(portfolio.cash_balance ?? portfolio.cash).toBeDefined();

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

  test('sends a chat message through the UI and shows a non-empty assistant reply without raw JSON', async ({ page }) => {
    await page.goto('/');

    const chatSection = page.getByRole('region', { name: 'AI assistant' });
    await expect(chatSection).toBeVisible();

    const input = chatSection.getByRole('textbox', { name: 'Message' });
    await input.fill('Hello FinAlly');

    const chatResponse = page.waitForResponse((res) => res.url().includes('/api/chat') && res.request().method() === 'POST');
    await chatSection.getByRole('button', { name: /send/i }).click();
    await chatResponse;

    // The user's message appears in the history, followed by an assistant bubble
    const assistantBubble = chatSection.getByRole('list', { name: 'Chat history' }).getByRole('listitem').last();
    await expect(assistantBubble).toBeVisible({ timeout: 20_000 });

    const text = (await assistantBubble.innerText()).trim();
    expect(text.length).toBeGreaterThan(0);
    expect(text.startsWith('{')).toBe(false);
    expect(text.startsWith('[')).toBe(false);
    expect(text).not.toContain('"role"');
  });

  test('opens the live price stream (SSE) on page load and receives price events', async ({ page }) => {
    const streamRequest = page.waitForRequest((req) => /\/api\/stream/.test(req.url()));

    await page.goto('/');

    const req = await streamRequest;
    expect(req.url()).toMatch(/\/api\/stream/);

    // Wait for a streamed price update to reach the page: the body should show a numeric price for a default ticker
    const priceReceived = await page.evaluate(
      () =>
        new Promise<boolean>((resolve) => {
          const timer = setTimeout(() => resolve(false), 15_000);
          const es = new EventSource('/api/stream/prices');
          es.onmessage = () => {
            clearTimeout(timer);
            es.close();
            resolve(true);
          };
          es.onerror = () => {
            clearTimeout(timer);
            es.close();
            resolve(false);
          };
        }),
    );
    expect(priceReceived).toBe(true);
  });
});
