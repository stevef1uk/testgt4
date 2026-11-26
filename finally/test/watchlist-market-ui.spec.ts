import { test, expect } from "@playwright/test";
import { DashboardPage } from "./pages/dashboard.page";

// Watchlist & market UI acceptance (SPEC: watchlist-market-ui phase).
// Uses only selectors exposed by DashboardPage (components in finally/frontend/components/).

test.describe("watchlist-market-ui", () => {
  test("market overview region is visible on load", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await expect(dashboard.marketOverview).toBeVisible();
  });

  test("watchlist ticker input and add button accept a new ticker", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await expect(dashboard.tickerInput).toBeVisible();
    await dashboard.tickerInput.fill("NFLX");
    await expect(dashboard.tickerInput).toHaveValue("NFLX");
    await dashboard.addButton.click();
    await expect(dashboard.watchlistRow("NFLX")).toBeVisible();
  });

  test("refresh button in header is enabled and clickable", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await expect(dashboard.refreshButton).toBeEnabled();
    await dashboard.refreshButton.click();
    await expect(dashboard.header).toBeVisible();
  });
});