import { Activity, BarChart3, Newspaper, ShieldAlert } from "lucide-react";
import { RiskBadge } from "../components/RiskBadge";
import { Sparkline } from "../components/Sparkline";
import { marketTiles, sparklinePoints } from "../data/mockData";

interface AssetDeepDiveProps {
  symbol: string;
}

export function AssetDeepDive({ symbol }: AssetDeepDiveProps) {
  const asset = marketTiles.find((tile) => tile.symbol === symbol) ?? marketTiles[0];

  return (
    <div className="space-y-5">
      <section className="atlas-panel p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase text-atlas-cyan">Asset Deep Dive</p>
            <div className="mt-1 flex items-end gap-3">
              <h1 className="font-mono text-4xl font-semibold text-atlas-text">{asset.symbol}</h1>
              <p className="pb-1 text-lg text-atlas-muted">{asset.name}</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="rounded-md border border-atlas-line bg-atlas-void px-3 py-2 font-mono text-lg text-atlas-text">{asset.price}</div>
            <RiskBadge state={asset.riskScore > 70 ? "high" : asset.riskScore > 50 ? "caution" : "normal"} label={`Risk ${asset.riskScore}`} />
            <RiskBadge state="normal" label={`AI ${asset.aiScore}`} />
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(380px,0.85fr)]">
        <div className="atlas-panel p-5">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">Chart Workspace</h2>
            </div>
            <div className="flex gap-2">
              {["1D", "1W", "1M", "3M", "1Y"].map((item) => (
                <button key={item} className="atlas-chip" type="button">
                  {item}
                </button>
              ))}
            </div>
          </div>
          <div className="mt-5 h-[420px] rounded-md border border-atlas-line bg-atlas-void p-5">
            <Sparkline points={asset.direction === "down" ? [...sparklinePoints].reverse() : sparklinePoints} direction={asset.direction} />
            <div className="mt-8 grid h-[240px] grid-cols-12 items-end gap-2">
              {sparklinePoints.map((value, index) => (
                <div key={`${value}-${index}`} className="rounded-t-sm bg-atlas-cyan/20" style={{ height: `${value * 3}px` }} />
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">Research Lens</h2>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {["Overview", "Fundamentals", "Technicals", "News", "Sentiment", "Risks", "AI Thesis"].map((tab) => (
                <button key={tab} type="button" className="atlas-chip">
                  {tab}
                </button>
              ))}
            </div>
            <p className="mt-4 text-sm leading-6 text-atlas-muted">
              ATLAS sees {asset.symbol} as an active watch candidate. Current UI values are preview data until the FastAPI backend connects quote, filings, news, and risk services.
            </p>
          </section>

          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <ShieldAlert className="h-5 w-5 text-atlas-amber" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">AI Explanation</h2>
            </div>
            <div className="mt-4 space-y-3 text-sm leading-6 text-atlas-muted">
              <p>Confidence depends on source freshness, price behavior, news quality, and portfolio impact.</p>
              <p>Invalidation requires stale data, earnings risk, major unverified news, or risk-limit breach.</p>
              <p>Trade preparation stays separated from execution until production controls are configured.</p>
            </div>
          </section>
        </div>
      </section>

      <section className="atlas-panel p-5">
        <div className="mb-4 flex items-center gap-3">
          <Newspaper className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
          <h2 className="text-lg font-semibold text-atlas-text">Timeline</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          {["Quote refreshed", "AI thesis updated", "Risk engine scanned", "Audit trail ready"].map((item, index) => (
            <div key={item} className="rounded-md border border-atlas-line bg-white/[0.03] p-3">
              <p className="font-mono text-xs text-atlas-muted">T+0{index}</p>
              <p className="mt-2 text-sm text-atlas-text">{item}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
