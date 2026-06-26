import { AlertTriangle, BarChart3, ClipboardList, Radar } from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { MarketTile } from "../components/MarketTile";
import { RiskBadge } from "../components/RiskBadge";
import { Sparkline } from "../components/Sparkline";
import { commandMetrics, marketTiles, sparklinePoints } from "../data/mockData";

interface CommandCenterProps {
  onSelectAsset: (symbol: string) => void;
}

export function CommandCenter({ onSelectAsset }: CommandCenterProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-blue">System Overview</p>
          <h1 className="mt-1 text-2xl font-semibold text-atlas-text">Command Center</h1>
        </div>
        <RiskBadge state="blocked" label="Live execution locked" />
      </div>

      <section className="grid gap-4 md:grid-cols-2 2xl:grid-cols-6">
        {commandMetrics.map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.55fr)]">
        <div className="atlas-panel p-5">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-5 w-5 text-atlas-blue" aria-hidden="true" />
              <div>
                <h2 className="text-lg font-semibold text-atlas-text">Market Pulse</h2>
                <p className="text-sm text-atlas-muted">Index trend, breadth, and risk tone</p>
              </div>
            </div>
            <RiskBadge state="normal" label="Monitoring" />
          </div>
          <div className="mt-5 h-[260px] rounded-md border border-atlas-line bg-atlas-void p-5">
            <Sparkline points={sparklinePoints} direction="up" />
            <div className="mt-8 grid grid-cols-4 gap-3">
              {["Breadth 58%", "Volatility Normal", "Liquidity Good", "News Active"].map((item) => (
                <div key={item} className="rounded-md border border-atlas-line bg-white/[0.03] p-3 text-sm text-atlas-muted">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <Radar className="h-5 w-5 text-atlas-amber" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">Top Risks</h2>
            </div>
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between rounded-md border border-atlas-line p-3">
                <span className="text-sm text-atlas-muted">Broker connection</span>
                <RiskBadge state="blocked" label="Unknown" />
              </div>
              <div className="flex items-center justify-between rounded-md border border-atlas-line p-3">
                <span className="text-sm text-atlas-muted">Event restrictions</span>
                <RiskBadge state="caution" label="Required" />
              </div>
              <div className="flex items-center justify-between rounded-md border border-atlas-line p-3">
                <span className="text-sm text-atlas-muted">Data lineage</span>
                <RiskBadge state="normal" label="Enabled" />
              </div>
            </div>
          </section>

          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <ClipboardList className="h-5 w-5 text-atlas-blue" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">AI Briefing</h2>
            </div>
            <p className="mt-4 text-sm leading-6 text-atlas-muted">
              ATLAS is in research-first mode. The system can gather evidence, build trade ideas, and run risk checks, but live execution remains locked until production readiness is approved.
            </p>
          </section>
        </div>
      </section>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-atlas-amber" aria-hidden="true" />
          <h2 className="text-lg font-semibold text-atlas-text">Watchlist Movers</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
          {marketTiles.slice(0, 6).map((tile) => (
            <MarketTile key={tile.symbol} tile={tile} onSelect={onSelectAsset} />
          ))}
        </div>
      </section>
    </div>
  );
}
