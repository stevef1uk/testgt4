import { test, expect } from "@playwright/test";
import { ChatPage } from "../pages/chat.page";
import { PortfolioPage } from "../pages/portfolio.page";

// SPEC chat scenarios, run with LLM_MOCK=true so replies are deterministic.

test.describe("AI chat assistant", () => {
  test("sending a message shows a pending state, then a non-empty assistant reply", async ({ page }) => {
    const chat = new ChatPage(page);
    await chat.goto();

    await chat.input.fill("What is my cash balance?");
    await chat.sendButton.click();

    // While the request is in flight the controls are disabled (loading state).
    await expect(chat.input).toBeDisabled();
    await expect(chat.sendButton).toBeDisabled();

    // Then the assistant reply appears and is non-empty.
    const assistant = page.locator('li[data-role="assistant"]').last();
    await expect(assistant).toBeVisible();
    await expect(assistant).not.toHaveText(/^\s*$/);

    await expect(chat.input).toBeEnabled();
    await expect(chat.input).toHaveValue("");
  });

  test('"Buy 5 AAPL" confirms the trade and the portfolio shows the new position', async ({ page }) => {
    const chat = new ChatPage(page);
    const portfolio = new PortfolioPage(page);
    await chat.goto();

    await chat.sendMessage("Buy 5 AAPL");

    const reply = page.locator('li[data-role="assistant"]').last();
    await expect(reply).toContainText(/AAPL/i);
    await expect(reply).toContainText(/5/);

    await expect(portfolio.positionRow("AAPL")).toBeVisible();
  });

  test("mock mode returns the same output structure for the same input", async ({ page }) => {
    const chat = new ChatPage(page);
    await chat.goto();

    await chat.sendMessage("Buy 5 AAPL");
    const firstReply = page.locator('li[data-role="assistant"]').last();
    await expect(firstReply).not.toHaveText(/^\s*$/);
    const firstText = (await firstReply.textContent()) ?? "";

    await chat.sendMessage("Buy 5 AAPL");
    await expect(page.locator('li[data-role="assistant"]')).toHaveCount(2);
    const secondReply = page.locator('li[data-role="assistant"]').last();
    const secondText = (await secondReply.textContent()) ?? "";

    expect(secondText.length).toBeGreaterThan(0);
    expect(secondText.trim().split(/\s+/).length).toBe(firstText.trim().split(/\s+/).length);
  });
});