"use client";

import Watchlist from "./Watchlist";

export interface SidebarProps {
  apiBase?: string;
  onSelectTicker?: (ticker: string) => void;
}

export default function Sidebar({ apiBase = "", onSelectTicker }: SidebarProps) {
  return (
    <aside aria-label="Sidebar" className="flex w-72 flex-col gap-6 border-r border-gray-700 p-4">
      <Watchlist apiBase={apiBase} onSelect={onSelectTicker} />
    </aside>
  );
}