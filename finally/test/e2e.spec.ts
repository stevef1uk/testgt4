import { expect, test } from "@playwright/test";

test.describe("watchlist market API", () => {
  test("reports API readiness", async ({ request }) => {
    const response = await request.get("/api/health");

    expect(response.status()).toBe(200);
    await expect(response.json()).resolves.toEqual({ status: "ok" });
  });

  test("serves the dashboard entry point", async ({ page }) => {
    const response = await page.goto("/");

    expect(response).not.toBeNull();
    expect(response?.ok()).toBeTruthy();
  });
});