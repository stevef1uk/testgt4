import { Page, Locator } from "@playwright/test";

export class ChatPage {
  readonly page: Page;
  readonly input: Locator;
  readonly sendButton: Locator;
  readonly messages: Locator;

  constructor(page: Page) {
    this.page = page;
    this.input = page.getByLabel("Chat message");
    this.sendButton = page.getByRole("button", { name: "Send" });
    this.messages = page.locator("li[data-role]");
  }

  async goto(): Promise<void> {
    await this.page.goto("/");
  }

  async sendMessage(text: string): Promise<void> {
    await this.input.fill(text);
    await this.sendButton.click();
  }

  async lastAssistantReply(): Promise<string | null> {
    const replies = this.page.locator('li[data-role="assistant"]');
    const count = await replies.count();
    if (count === 0) return null;
    return replies.nth(count - 1).textContent();
  }
}