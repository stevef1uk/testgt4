"use client";

import Watchlist from "./Watchlist";

export interface SidebarProps {
  selectedTicker?: string;
  onSelect?: (ticker: string) => void;
}

export default function Sidebar({ selectedTicker, onSelect }: SidebarProps) {
  return (
    <aside aria-label="Sidebar" className="w-80 border-r border-gray-800 bg-[#0d1117] overflow-y-auto shrink-0">
      <Watchlist selectedTicker={selectedTicker} onSelect={onSelect} />
    </aside>
  );
}
