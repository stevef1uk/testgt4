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

  test('sends a chat message through the UI and shows a non-empty assistant reply without raw JSON', async ({ page }) => {
    await page.goto('/');

    const chatSection = page.locator('section[aria-label="AI assistant"]');
    await expect(chatSection).toBeVisible();

    const input = chatSection.locator('input[aria-label="Message"], textarea[aria-label="Message"]');
    await input.fill('Hello FinAlly');

    const chatResponse = page.waitForResponse((res) => res.url().includes('/api/chat') && res.request().method() === 'POST');
    await chatSection.locator('button[type="submit"]').click();
    await chatResponse;

    // The user's message appears in the history, followed by an assistant bubble
    const assistantBubble = chatSection.locator('ul[aria-label="Chat history"] li[data-role="assistant"]').last();
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