import { defineConfig, devices } from '@playwright/test';

// Base URL of the running FinAlly app. docker-compose.test.yml sets BASE_URL to
// http://app:8010 on the internal network; local runs default to the same port.
const baseURL = process.env.BASE_URL ?? 'http://127.0.0.1:8010';

export default defineConfig({
  testDir: '.',
  testMatch: '**/*.spec.ts',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});