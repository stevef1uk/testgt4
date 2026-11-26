import { test, expect } from '@playwright/test';

// SPEC section 2 (first launch): fresh start shows the default watchlist and starting cash.
const DEFAULT_TICKERS = [
  'AAPL',
  'GOOGL',
  'MSFT',
  'AMZN',
  'TSLA',
  'NVDA',
  'META',
  'JPM',
  'V',
  'NFLX',
];

test.describe('first launch', () => {
  test('shows the 10 default watchlist tickers', async ({ page }) => {
    await page.goto('/');
    for (const ticker of DEFAULT_TICKERS) {
      await expect(page.getByText(ticker, { exact: true }).first()).toBeVisible();
    }
  });

  test('shows $10,000 starting cash', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText(/\$\s?10,000(\.00)?/).first()).toBeVisible();
  });
});

test.describe('interactive behaviour', () => {
  test('adding a ticker through the UI updates the watchlist DOM', async ({ page }) => {
    await page.goto('/');
    const input = page.getByPlaceholder(/ticker/i).first();
    await input.fill('PYPL');
    await page.getByRole('button', { name: /add/i }).first().click();
    await expect(page.getByText('PYPL', { exact: true }).first()).toBeVisible();
  });
});