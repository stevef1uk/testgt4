import { test, expect } from "@playwright/test";
import { DashboardPage } from "../pages/dashboard.page";

// Default watchlist seeded by the backend (SPEC: ten tickers, $10,000.00 cash).
const DEFAULT_TICKERS = 10;
const STARTING_CASH = /\$\s?10,?000\.00/;
const EXTRA_TICKER = "PYPL";

test.describe("dashboard", () => {
  test.beforeEach(async ({ request }) => {
    await request.post("/api/reset").catch(() => {});
  });

  test("initial load shows ten watchlist tickers and starting cash", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await expect(dashboard.watchlist).toBeVisible();
    await expect(dashboard.watchlist.locator('[data-testid^="watchlist-row-"]')).toHaveCount(
      DEFAULT_TICKERS,
    );
    await expect(page.getByTestId("header-cash-balance")).toHaveText(STARTING_CASH);
  });

  test("all core UI components are mounted and visible simultaneously", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await expect(page.getByRole("heading", { name: "FinAlly" })).toBeVisible();
    await expect(page.getByTestId("connection-status")).toBeVisible();
    await expect(page.getByTestId("cash-balance")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Watchlist" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Watchlist" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Market overview" })).toBeVisible();
    await expect(page.getByLabel(/price chart/i)).toBeVisible();
    await expect(page.getByTestId("portfolio-summary")).toBeVisible();
    await expect(page.getByTestId("positions-table")).toBeVisible();
    await expect(page.getByTestId("trading-panel")).toBeVisible();
    await expect(page.getByLabel("Chat assistant")).toBeVisible();
  });

  test("adding a ticker through the UI adds a watchlist row", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await expect(dashboard.watchlistRow(EXTRA_TICKER)).toHaveCount(0);
    await dashboard.addTicker(EXTRA_TICKER);
    await expect(dashboard.watchlistRow(EXTRA_TICKER)).toBeVisible();
  });

  test("removing a ticker through the UI removes its watchlist row", async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await dashboard.addTicker(EXTRA_TICKER);
    await expect(dashboard.watchlistRow(EXTRA_TICKER)).toBeVisible();

    await dashboard.removeTicker(EXTRA_TICKER);
    await expect(dashboard.watchlistRow(EXTRA_TICKER)).toHaveCount(0);
  });
});
