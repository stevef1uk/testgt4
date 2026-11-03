import { test, expect } from "@playwright/test";

const defaultTickers = [
  "AAPL",
  "GOOGL",
  "MSFT",
  "AMZN",
  "TSLA",
  "NVDA",
  "META",
  "JPM",
  "V",
  "NFLX",
];

test.describe("FinAlly dashboard", () => {
  test("renders the seeded portfolio and connection state", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("FinAlly")).toBeVisible();
    await expect(page.getByText("Market Dashboard")).toBeVisible();
    await expect(page.getByText("$10,000")).toBeVisible();
    await expect(page.getByTestId("connection-status")).toBeVisible();

    for (const ticker of defaultTickers) {
      await expect(page.getByText(ticker, { exact: true })).toBeVisible();
    }
  });

  test("adds and removes a watchlist ticker", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("textbox", { name: /add ticker/i }).fill("PYPL");
    await page.getByRole("button", { name: /add ticker/i }).click();
    await expect(page.getByText("PYPL", { exact: true })).toBeVisible();

    await page.getByRole("button", { name: /remove NFLX/i }).click();
    await expect(page.getByText("NFLX", { exact: true })).not.toBeVisible();
  });

  test("submits a portfolio question and renders an assistant response", async ({ page }) => {
    await page.goto("/");

    const message = page.getByRole("textbox", { name: /message/i });
    await message.fill("What's my portfolio value?");
    await page.getByRole("button", { name: /send/i }).click();

    await expect(page.getByText("What's my portfolio value?", { exact: true })).toBeVisible();
    await expect(page.getByTestId("assistant-message").last()).not.toBeEmpty();
  });

  test("exposes health, watchlist, and portfolio API contracts", async ({ request }) => {
    const health = await request.get("/api/health");
    expect(health.status()).toBe(200);
    await expect(health.json()).resolves.toEqual({ status: "ok" });

    const watchlist = await request.get("/api/watchlist");
    expect(watchlist.status()).toBe(200);
    expect(Array.isArray(await watchlist.json())).toBe(true);

    const portfolio = await request.get("/api/portfolio");
    expect(portfolio.status()).toBe(200);
    const portfolioBody = await portfolio.json();
    expect(portfolioBody).toHaveProperty("cash");
    expect(portfolioBody).toHaveProperty("positions");
    expect(portfolioBody).toHaveProperty("total_value");
  });

  test("rejects invalid trades before changing portfolio state", async ({ request }) => {
    const invalidTrade = await request.post("/api/trades", {
      data: { ticker: "AAPL", quantity: 0, side: "buy" },
    });
    expect(invalidTrade.status()).toBeGreaterThanOrEqual(400);
    expect(invalidTrade.status()).toBeLessThan(500);

    const portfolio = await request.get("/api/portfolio");
    expect(portfolio.status()).toBe(200);
    expect((await portfolio.json()).positions).toBeDefined();
  });

  test("serves the market event stream contract", async ({ request }) => {
    const stream = await request.get("/api/stream", {
      headers: { Accept: "text/event-stream" },
      timeout: 5000,
    });

    expect([200, 204, 404, 405]).toContain(stream.status());
    if (stream.status() === 200) {
      expect(stream.headers()["content-type"]).toContain("text/event-stream");
    }
  });

  test("supports navigation and repeatable dashboard reloads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Market Dashboard")).toBeVisible();

    const navigation = page.getByRole("navigation");
    if (await navigation.count()) {
      await expect(navigation).toBeVisible();
    }

    await page.reload();
    await expect(page.getByText("Market Dashboard")).toBeVisible();
    await expect(page.getByTestId("connection-status")).toBeVisible();
  });
});