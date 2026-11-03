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
  test("loads the real dashboard and seeded portfolio", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Market Dashboard")).toBeVisible();
    await expect(page.getByText("FinAlly")).toBeVisible();
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

  test("submits a mocked portfolio question", async ({ page }) => {
    await page.goto("/");

    const message = page.getByRole("textbox", { name: /message/i });
    await message.fill("What's my portfolio value?");
    await page.getByRole("button", { name: /send/i }).click();

    await expect(page.getByText("What's my portfolio value?", { exact: true })).toBeVisible();
    await expect(page.getByTestId("assistant-message").last()).not.toBeEmpty();
  });
});