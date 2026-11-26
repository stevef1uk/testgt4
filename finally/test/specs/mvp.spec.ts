import { test, expect } from '@playwright/test';

// SPEC section 2 (first launch) and MVP core flow: default watchlist, starting cash,
// and adding a ticker through the real UI controls.

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

test.describe('MVP: first launch', () => {
  test('renders the 10 default watchlist tickers', async ({ page }) => {
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

test.describe('MVP: watchlist interaction', () => {
  test('adding a ticker through the input and button appears in the watchlist', async ({ page }) => {
    await page.goto('/');
    const input = page.getByPlaceholder(/ticker/i).first();
    await input.fill('PYPL');
    await page.getByRole('button', { name: /add/i }).first().click();
    await expect(page.getByText('PYPL', { exact: true }).first()).toBeVisible();
  });

  test('adding a ticker clears the input field', async ({ page }) => {
    await page.goto('/');
    const input = page.getByPlaceholder(/ticker/i).first();
    await input.fill('PYPL');
    await page.getByRole('button', { name: /add/i }).first().click();
    await expect(page.getByText('PYPL', { exact: true }).first()).toBeVisible();
    await expect(input).toHaveValue('');
  });
});