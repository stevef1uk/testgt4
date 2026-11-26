import { test, expect } from "@playwright/test";
import { PortfolioPage } from "../pages/portfolio.page";

test.describe("portfolio", () => {
  test("shows the positions table and cash balance on load", async ({ page }) => {
    const portfolio = new PortfolioPage(page);
    await portfolio.goto();

    await expect(portfolio.positionsTable).toBeVisible();
    await expect(portfolio.cashText()).toBeVisible();
  });

  test("position rows can be looked up by ticker", async ({ page }) => {
    const portfolio = new PortfolioPage(page);
    await portfolio.goto();

    await expect(portfolio.positionsTable.getByRole("row").first()).toBeVisible();
    await expect(portfolio.positionRow("AAPL").first()).toContainText("AAPL");
  });

  test("empty portfolio starts with $10,000 cash", async ({ page }) => {
    const portfolio = new PortfolioPage(page);
    await portfolio.goto();

    await expect(portfolio.cashText()).toContainText("$10,000");
  });
});