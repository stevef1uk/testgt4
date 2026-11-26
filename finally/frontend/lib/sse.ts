export const PRICE_STREAM_URL = "/api/stream/prices";

export interface PriceEvent {
  ticker: string;
  price: number;
  previous_price: number;
  change: number;
  change_percent: number;
  direction: "up" | "down" | "flat";
  updated_at: string;
}

export interface PriceStreamOptions {
  url?: string;
  onPrice: (event: PriceEvent) => void;
  onError?: (error: Event) => void;
}

export interface PriceStreamHandle {
  close: () => void;
}

export function openPriceStream(options: PriceStreamOptions): PriceStreamHandle {
  const source = new EventSource(options.url ?? PRICE_STREAM_URL);

  const handler = (msg: MessageEvent<string>) => {
    try {
      const parsed = JSON.parse(msg.data) as PriceEvent;
      options.onPrice(parsed);
    } catch {
      // Ignore malformed frames; the next event will carry fresh data.
    }
  };

  source.onmessage = handler;
  source.addEventListener("price", handler as EventListener);

  source.onerror = (ev: Event) => {
    options.onError?.(ev);
  };

  return {
    close: () => source.close(),
  };
}
