import { test, expect } from "@playwright/test";
import { TradePage } from "../pages/trade.page";

test.describe("Trading panel", () => {
  test("sell button submits a sell and reports the outcome", async ({ page }) => {
    await page.route("**/api/portfolio/trade", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" })
    );

    const trade = new TradePage(page);
    await trade.goto("/");

    await trade.sell("MSFT", 3);

    await expect(trade.status).toHaveText(/SELL 3 MSFT filled/);
  });
});