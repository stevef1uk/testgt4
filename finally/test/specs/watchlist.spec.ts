import { test, expect } from "@playwright/test";
import { WatchlistPage } from "../pages/watchlist.page";

test.describe("Watchlist", () => {
  test("adding a ticker adds a row to the watchlist", async ({ page }) => {
    const watchlist = new WatchlistPage(page);
    await watchlist.goto("/");

    await watchlist.addTicker("AAPL");

    await expect(watchlist.rowFor("AAPL")).toBeVisible();
  });
});