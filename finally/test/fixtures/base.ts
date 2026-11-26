import { test as base, expect } from '@playwright/test';
import { BACKEND_BASE_URL, getJson, postJson, type ApiResponse } from '../api/helpers';

/**
 * Shared Playwright fixtures for the end-to-end suite.
 * Specs import `test` and `expect` from this module so every spec gets the
 * same backend wiring (see finally/test/api/helpers.ts).
 */
export type ApiFixture = {
  baseUrl: string;
  get: <T = unknown>(path: string) => Promise<ApiResponse<T>>;
  post: <T = unknown>(path: string, payload: unknown) => Promise<ApiResponse<T>>;
};

export const test = base.extend<{ api: ApiFixture }>({
  api: async ({}, use) => {
    await use({
      baseUrl: BACKEND_BASE_URL,
      get: (path) => getJson(path),
      post: (path, payload) => postJson(path, payload),
    });
  },
});

export { expect };