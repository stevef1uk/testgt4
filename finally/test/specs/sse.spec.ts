import { test, expect } from '@playwright/test';

// SSE: the dashboard must open a server-sent event stream on load.
// The endpoint path is not hardcoded; the test observes any response served
// with Content-Type text/event-stream triggered by the page.

test.describe('SSE stream', () => {
  test('page opens a text/event-stream connection on load', async ({ page }) => {
    const streamResponse = page.waitForResponse(
      (response) =>
        (response.headers()['content-type'] || '').includes('text/event-stream'),
      { timeout: 15000 },
    );

    await page.goto('/');

    const response = await streamResponse;
    expect(response.ok()).toBeTruthy();
    expect(response.headers()['content-type']).toContain('text/event-stream');
  });

  test('stream connection is established without a page error', async ({ page }) => {
    const pageErrors: Error[] = [];
    page.on('pageerror', (err) => pageErrors.push(err));

    const streamResponse = page.waitForResponse(
      (response) =>
        (response.headers()['content-type'] || '').includes('text/event-stream'),
      { timeout: 15000 },
    );

    await page.goto('/');
    await streamResponse;

    expect(pageErrors).toEqual([]);
  });
});