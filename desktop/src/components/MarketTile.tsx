import { Activity, Newspaper } from "lucide-react";
import type { MarketTileData } from "../types";

interface MarketTileProps {
  tile: MarketTileData;
  onSelect?: (symbol: string) => void;
}

export function MarketTile({ tile, onSelect }: MarketTileProps) {
  const directionClass =
    tile.direction === "up"
      ? "border-atlas-green/40 bg-atlas-green/10 text-atlas-green"
      : tile.direction === "down"
        ? "border-atlas-red/40 bg-atlas-red/10 text-atlas-red"
        : "border-atlas-cyan/40 bg-atlas-cyan/10 text-atlas-cyan";

  return (
    <button
      type="button"
      className="atlas-panel group flex min-h-[164px] flex-col justify-between p-4 text-left transition hover:border-atlas-cyan/70 hover:shadow-glow"
      onClick={() => onSelect?.(tile.symbol)}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="font-mono text-xl font-semibold text-atlas-text">{tile.symbol}</div>
          <div className="mt-1 max-w-[170px] truncate text-xs text-atlas-muted">{tile.name}</div>
        </div>
        <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${directionClass}`}>{tile.change}</span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-atlas-muted">
        <div>
          <p>Price</p>
          <p className="font-mono text-sm text-atlas-text">{tile.price}</p>
        </div>
        <div>
          <p>Volume</p>
          <p className="text-sm text-atlas-text">{tile.volume}</p>
        </div>
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
          <span>AI {tile.aiScore}</span>
        </div>
        <div className="flex items-center gap-2">
          <Newspaper className="h-4 w-4 text-atlas-amber" aria-hidden="true" />
          <span>{tile.newsSignal}</span>
        </div>
      </div>
    </button>
  );
}
