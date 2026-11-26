import { Page, Locator } from "@playwright/test";

/**
 * Page object for the trading form (TradingPanel component).
 * Selectors use the data-testid attributes defined in TradingPanel.tsx.
 */
export class TradePage {
  readonly page: Page;
  readonly panel: Locator;
  readonly ticker: Locator;
  readonly quantity: Locator;
  readonly buyButton: Locator;
  readonly sellButton: Locator;
  readonly status: Locator;

  constructor(page: Page) {
    this.page = page;
    this.panel = page.getByTestId("trading-panel");
    this.ticker = page.getByTestId("trade-ticker");
    this.quantity = page.getByTestId("trade-quantity");
    this.buyButton = page.getByTestId("trade-buy");
    this.sellButton = page.getByTestId("trade-sell");
    this.status = page.getByTestId("trade-status");
  }

  async goto(path: string = "/"): Promise<void> {
    await this.page.goto(path);
  }

  async fillTicker(symbol: string): Promise<void> {
    await this.ticker.fill(symbol);
  }

  async fillQuantity(quantity: number): Promise<void> {
    await this.quantity.fill(String(quantity));
  }

  async buy(symbol: string, quantity: number): Promise<void> {
    await this.fillTicker(symbol);
    await this.fillQuantity(quantity);
    await this.buyButton.click();
  }

  async sell(symbol: string, quantity: number): Promise<void> {
    await this.fillTicker(symbol);
    await this.fillQuantity(quantity);
    await this.sellButton.click();
  }

  async statusText(): Promise<string> {
    return (await this.status.textContent())?.trim() ?? "";
  }
}