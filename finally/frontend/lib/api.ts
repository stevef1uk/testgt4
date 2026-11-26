export const API_BASE = "/api";

export interface WatchlistItem {
  ticker: string;
  price: number;
  previous_price: number;
  change: number;
  change_percent: number;
  direction: "up" | "down" | "flat";
  updated_at: string;
}

export interface WatchlistResponse {
  tickers: WatchlistItem[];
}

export interface PortfolioPosition {
  ticker: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  unrealized_pnl: number;
}

export interface PortfolioSummary {
  cash_balance: number;
  total_value: number;
  unrealized_pnl: number;
  positions: PortfolioPosition[];
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(`Request failed (${status}): ${message}`);
    this.name = "ApiError";
    this.status = status;
  }
}

async function readErrorMessage(res: Response): Promise<string> {
  const fallback = res.statusText || "Unknown error";
  try {
    const body = await res.text();
    if (!body) return fallback;
    try {
      const parsed = JSON.parse(body) as { detail?: unknown; error?: unknown; message?: unknown };
      const msg = parsed.detail ?? parsed.error ?? parsed.message;
      return typeof msg === "string" && msg.length > 0 ? msg : body;
    } catch {
      return body;
    }
  } catch {
    return fallback;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    throw new ApiError(res.status, await readErrorMessage(res));
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export function getWatchlist(): Promise<WatchlistResponse> {
  return request<WatchlistResponse>("/watchlist");
}

export function addWatchlistTicker(ticker: string): Promise<WatchlistResponse> {
  return request<WatchlistResponse>("/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker: ticker.toUpperCase() }),
  });
}

export function removeWatchlistTicker(ticker: string): Promise<WatchlistResponse> {
  return request<WatchlistResponse>(
    `/watchlist/${encodeURIComponent(ticker.toUpperCase())}`,
    { method: "DELETE" },
  );
}

export function getPortfolio(): Promise<PortfolioSummary> {
  return request<PortfolioSummary>("/portfolio");
}