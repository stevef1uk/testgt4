import { type Locator, type Page, expect } from "@playwright/test";

/**
 * Page object for the FinAlly dashboard.
 * Selectors come from the components implemented in finally/frontend/components/.
 */
export class DashboardPage {
  readonly page: Page;
  readonly header: Locator;
  readonly sidebar: Locator;
  readonly watchlist: Locator;
  readonly marketOverview: Locator;
  readonly tickerInput: Locator;
  readonly addButton: Locator;
  readonly refreshButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.header = page.locator("header");
    this.sidebar = page.getByLabel("Sidebar");
    this.watchlist = page.getByRole("region", { name: "Watchlist" });
    this.marketOverview = page.getByRole("region", { name: "Market overview" });
    this.tickerInput = this.watchlist.getByLabel("Watchlist ticker");
    this.addButton = this.watchlist.getByRole("button", { name: "Add", exact: true });
    this.refreshButton = this.header.getByRole("button", { name: "Refresh" });
  }

  async goto(): Promise<void> {
    await this.page.goto("/");
    await expect(this.header).toBeVisible();
  }

  watchlistRow(ticker: string): Locator {
    return this.page.getByTestId(`watchlist-row-${ticker}`);
  }

  removeButton(ticker: string): Locator {
    return this.page.getByRole("button", { name: `Remove ${ticker}` });
  }

  async addTicker(ticker: string): Promise<void> {
    await this.tickerInput.fill(ticker);
    await this.addButton.click();
  }

  async removeTicker(ticker: string): Promise<void> {
    await this.removeButton(ticker).click();
  }
}