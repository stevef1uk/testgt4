"use client";

export interface MarketOverviewItem {
  ticker: string;
  price: number;
  change_percent?: number | null;
}

export interface MarketOverviewProps {
  items: MarketOverviewItem[];
  onSelect?: (ticker: string) => void;
}

export default function MarketOverview({ items, onSelect }: MarketOverviewProps) {
  return (
    <section aria-label="Market overview" className="flex flex-col gap-2">
      <h2 className="text-sm font-semibold uppercase text-gray-400">Market</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-400">No prices yet.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400">
              <th className="py-1 font-normal">Ticker</th>
              <th className="py-1 text-right font-normal">Price</th>
              <th className="py-1 text-right font-normal">Change</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const change = item.change_percent ?? null;
              return (
                <tr key={item.ticker} className="border-t border-gray-800">
                  <td className="py-1">
                    <button
                      type="button"
                      onClick={() => onSelect?.(item.ticker)}
                      className="font-mono hover:underline"
                    >
                      {item.ticker}
                    </button>
                  </td>
                  <td className="py-1 text-right font-mono">${item.price.toFixed(2)}</td>
                  <td
                    className={`py-1 text-right font-mono ${
                      change === null ? "" : change >= 0 ? "text-green-400" : "text-red-400"
                    }`}
                  >
                    {change === null ? "—" : `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}