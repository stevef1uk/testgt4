import { test, expect } from "@playwright/test";
import { TradePage } from "./pages/trade.page";

test.describe("Portfolio visualisation and trading", () => {
  test("renders portfolio summary, heatmap, P&L chart and positions table", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByTestId("portfolio-summary")).toBeVisible();
    await expect(page.getByTestId("portfolio-heatmap")).toBeVisible();
    await expect(page.getByTestId("pnl-chart")).toBeVisible();
    await expect(page.getByTestId("positions-table")).toBeVisible();
  });

  test("trading panel submits a buy and reports the outcome", async ({ page }) => {
    await page.route("**/api/portfolio/trade", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" })
    );

    const trade = new TradePage(page);
    await trade.goto("/");
    await expect(trade.panel).toBeVisible();

    await trade.buy("AAPL", 2);

    await expect(trade.status).toHaveText(/BUY 2 AAPL filled/);
  });
});