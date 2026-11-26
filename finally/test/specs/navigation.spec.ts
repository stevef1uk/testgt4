import { test, expect } from '@playwright/test';

// Navigation: the app is served at the root URL, and the watchlist state is
// reachable again after leaving and returning to the page.

const DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT'];

test.describe('navigation', () => {
  test('root URL loads the dashboard with default tickers', async ({ page }) => {
    const response = await page.goto('/');
    expect(response?.ok()).toBeTruthy();
    for (const ticker of DEFAULT_TICKERS) {
      await expect(page.getByText(ticker, { exact: true }).first()).toBeVisible();
    }
  });

  test('returning to the root after navigating away restores the watchlist', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('AAPL', { exact: true }).first()).toBeVisible();

    await page.goto('/does-not-exist');
    await page.goto('/');

    for (const ticker of DEFAULT_TICKERS) {
      await expect(page.getByText(ticker, { exact: true }).first()).toBeVisible();
    }
  });

  test('browser back returns to the watchlist view', async ({ page }) => {
    await page.goto('/');
    await page.goto('/does-not-exist');
    await page.goBack();
    await expect(page.getByText('AAPL', { exact: true }).first()).toBeVisible();
  });
});