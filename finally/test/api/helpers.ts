/**
 * Shared API helpers for Playwright end-to-end tests.
 * Talks to the backend running on the host (see .env BACKEND_HOST / BACKEND_PORT).
 */

export const BACKEND_BASE_URL: string =
  process.env.BACKEND_BASE_URL ??
  `http://${process.env.BACKEND_HOST ?? '127.0.0.1'}:${process.env.BACKEND_PORT ?? '8000'}`;

export interface ApiResponse<T = unknown> {
  status: number;
  contentType: string | null;
  body: T;
}

/**
 * Perform a JSON request against the backend and return the decoded body.
 * Throws if the response is not ok, so callers can rely on a 2xx result.
 */
export async function apiRequest<T = unknown>(
  path: string,
  init: RequestInit = {},
): Promise<ApiResponse<T>> {
  const url = path.startsWith('http') ? path : `${BACKEND_BASE_URL}${path}`;
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(init.body ? { 'Content-Type': 'application/json' } : {}),
    ...((init.headers as Record<string, string>) ?? {}),
  };
  const res = await fetch(url, { ...init, headers });
  const contentType = res.headers.get('content-type');
  const text = await res.text();
  const body = (text && contentType?.includes('application/json') ? JSON.parse(text) : text) as T;
  if (!res.ok) {
    throw new Error(`API ${init.method ?? 'GET'} ${path} failed: ${res.status} ${text}`);
  }
  return { status: res.status, contentType, body };
}

export function getJson<T = unknown>(path: string): Promise<ApiResponse<T>> {
  return apiRequest<T>(path, { method: 'GET' });
}

export function postJson<T = unknown>(path: string, payload: unknown): Promise<ApiResponse<T>> {
  return apiRequest<T>(path, { method: 'POST', body: JSON.stringify(payload) });
}