import { Page, Locator } from "@playwright/test";

export class PortfolioPage {
  readonly page: Page;
  readonly positionsTable: Locator;

  constructor(page: Page) {
    this.page = page;
    this.positionsTable = page.getByTestId("positions-table");
  }

  async goto(): Promise<void> {
    await this.page.goto("/");
  }

  cashText(): Locator {
    return this.page.getByTestId("header-cash-balance");
  }

  positionRow(ticker: string): Locator {
    return this.page
      .locator(`[data-testid="positions-table"] [data-ticker="${ticker}"]`)
      .or(this.page.locator(`[data-testid="watchlist-row-${ticker}"]`))
      .first();
  }
}
