import { test, expect } from '@playwright/test';

// Acceptance (te-dom): dark theme from SPEC Section 2 applied to the rendered dashboard,
// with real dashboard content visible.
// Foreground token #e6edf3 = rgb(230, 237, 243); background token #0d1117 = rgb(13, 17, 23).
test.describe('application polish', () => {
  test.beforeEach(async ({ request }) => {
    await request.post('/api/reset').catch(() => {});
  });

  test('body renders the SPEC dark theme colours', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('body')).toBeVisible();

    // Wait for the stylesheet to apply the body colour before reading it.
    await expect
      .poll(async () => page.evaluate(() => getComputedStyle(document.body).color))
      .toBe('rgb(230, 237, 243)');

    const background = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    expect(background).toBe('rgb(13, 17, 23)');
  });

  test('dashboard shows real content: brand, watchlist and cash balance', async ({ page }) => {
    await page.goto('/');

    // Assert only text the rendered page actually contains (see finally/frontend/app/page.tsx).
    await expect(page.getByRole('heading', { name: 'FinAlly' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Watchlist' })).toBeVisible();
    await expect(page.getByTestId('cash-balance')).toContainText(/\$\s?10,?000\.00/);
  });

  test('selecting a ticker and clicking Buy updates the trade status', async ({ page }) => {
    await page.goto('/');

    // Select MSFT from the watchlist (real ticker button in page.tsx).
    await page.getByRole('button', { name: 'MSFT', exact: true }).click();
    await expect(page.getByText('Selected: MSFT')).toBeVisible();
    await expect(page.getByRole('button', { name: 'MSFT', exact: true })).toHaveAttribute('aria-pressed', 'true');

    // Enter a quantity and click Buy; the status region must reflect the trade.
    await page.getByRole('spinbutton', { name: 'Quantity' }).fill('2');
    await page.getByRole('button', { name: 'Buy', exact: true }).click();
    await expect(page.getByRole('status')).toHaveText('Bought 2 MSFT');
  });

  test('clicking Sell with an invalid quantity shows a validation message', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('spinbutton', { name: 'Quantity' }).fill('0');
    await page.getByRole('button', { name: 'Sell', exact: true }).click();
    await expect(page.getByRole('status')).toHaveText('Enter a positive quantity');
  });
});