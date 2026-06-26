import { Grid3X3, SlidersHorizontal } from "lucide-react";
import { MarketTile } from "../components/MarketTile";
import { RiskBadge } from "../components/RiskBadge";
import { marketTiles } from "../data/mockData";

interface MarketMapProps {
  onSelectAsset: (symbol: string) => void;
}

export function MarketMap({ onSelectAsset }: MarketMapProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-cyan">Multi-Dimensional View</p>
          <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Market Map</h1>
        </div>
        <button className="atlas-button" type="button">
          <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
          Filters
        </button>
      </div>

      <section className="atlas-panel p-4">
        <div className="flex flex-wrap items-center gap-2">
          {["Sector heatmap", "Watchlist", "Volatility", "Momentum", "News intensity", "AI opportunity"].map((filter) => (
            <button key={filter} type="button" className="atlas-chip">
              {filter}
            </button>
          ))}
          <RiskBadge state="caution" label="Preview data" />
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        {marketTiles.map((tile) => (
          <MarketTile key={tile.symbol} tile={tile} onSelect={onSelectAsset} />
        ))}
      </section>

      <section className="atlas-panel p-5">
        <div className="flex items-center gap-3">
          <Grid3X3 className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
          <h2 className="text-lg font-semibold text-atlas-text">Map Legend</h2>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-6">
          {[
            ["Positive", "bg-atlas-green"],
            ["Negative", "bg-atlas-red"],
            ["Caution", "bg-atlas-amber"],
            ["Neutral", "bg-atlas-cyan"],
            ["AI attention", "bg-atlas-violet"],
            ["No reliable data", "bg-atlas-muted"]
          ].map(([label, color]) => (
            <div key={label} className="flex items-center gap-2 rounded-md border border-atlas-line p-3 text-sm text-atlas-muted">
              <span className={`h-2.5 w-2.5 rounded-sm ${color}`} />
              {label}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
