import { Page, Locator } from "@playwright/test";

/**
 * Page object for the watchlist (watchlist-market-ui phase).
 * Uses role/label-based locators so it does not depend on undocumented DOM IDs.
 */
export class WatchlistPage {
  readonly page: Page;
  readonly tickerInput: Locator;
  readonly addButton: Locator;
  readonly rows: Locator;

  constructor(page: Page) {
    this.page = page;
    this.tickerInput = page.getByLabel(/ticker/i);
    this.addButton = page.getByRole("button", { name: /add/i });
    this.rows = page.getByRole("row");
  }

  async goto(path: string = "/"): Promise<void> {
    await this.page.goto(path);
  }

  async addTicker(symbol: string): Promise<void> {
    await this.tickerInput.fill(symbol);
    await this.addButton.click();
  }

  async rowCount(): Promise<number> {
    return this.rows.count();
  }

  rowFor(symbol: string): Locator {
    return this.page.locator('section[aria-label="Watchlist"]').getByRole("row", { name: new RegExp(symbol, "i") });
  }
}