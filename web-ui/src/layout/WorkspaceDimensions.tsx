import { BrainCircuit, Clock3, Crosshair, Gauge, Layers3, ShieldAlert } from "lucide-react";
import type { AppContext, RiskState, ViewId } from "../types";

interface WorkspaceDimensionsProps {
  activeView: ViewId;
  context: AppContext;
  onCommandOpen: () => void;
}

const timeFrames = ["Today", "1W", "1M", "3M", "1Y"];
const assetScopes = ["Stock", "ETF", "Watchlist", "Portfolio"];
const lenses = ["AI", "Technical", "Fundamental", "News", "Risk"];
const modes = ["Research", "Backtest", "Paper", "Live"];

function selectedClass(selected: boolean) {
  return selected
    ? "border-atlas-blue/60 bg-atlas-blue/10 text-atlas-text"
    : "border-atlas-line bg-white/[0.02] text-atlas-muted hover:border-atlas-blue/50 hover:text-atlas-text";
}

function RiskStateDot({ state }: { state: RiskState }) {
  const color =
    state === "normal"
      ? "bg-atlas-green"
      : state === "caution"
        ? "bg-atlas-amber"
        : state === "high"
          ? "bg-atlas-red"
          : "bg-atlas-red";

  return <span className={`h-2 w-2 rounded-full ${color}`} aria-hidden="true" />;
}

export function WorkspaceDimensions({ activeView, context, onCommandOpen }: WorkspaceDimensionsProps) {
  const selectedLens = activeView === "risk-center" ? "Risk" : activeView === "research-lab" ? "AI" : "Technical";
  const selectedMode = activeView === "paper-trading" ? "Paper" : activeView === "live-trading" ? "Live" : "Research";
  const confidence = context.mode === "Live" ? "Unknown" : "Medium";

  return (
    <section className="mb-4 rounded-md border border-atlas-line bg-atlas-deck/80 px-3 py-2">
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" className="atlas-button h-8" onClick={onCommandOpen}>
          <Crosshair className="h-4 w-4" aria-hidden="true" />
          Command Mode
        </button>

        <div className="flex items-center gap-1 rounded-md border border-atlas-line bg-white/[0.02] px-2 py-1">
          <Clock3 className="h-4 w-4 text-atlas-muted" aria-hidden="true" />
          {timeFrames.map((item) => (
            <button key={item} type="button" className={`h-7 rounded-md border px-2 text-xs transition ${selectedClass(item === "Today")}`}>
              {item}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1 rounded-md border border-atlas-line bg-white/[0.02] px-2 py-1">
          <Layers3 className="h-4 w-4 text-atlas-muted" aria-hidden="true" />
          {assetScopes.map((item) => (
            <button
              key={item}
              type="button"
              className={`h-7 rounded-md border px-2 text-xs transition ${selectedClass(item === "Stock")}`}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1 rounded-md border border-atlas-line bg-white/[0.02] px-2 py-1">
          <BrainCircuit className="h-4 w-4 text-atlas-muted" aria-hidden="true" />
          {lenses.map((item) => (
            <button key={item} type="button" className={`h-7 rounded-md border px-2 text-xs transition ${selectedClass(item === selectedLens)}`}>
              {item}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1 rounded-md border border-atlas-line bg-white/[0.02] px-2 py-1">
          <Gauge className="h-4 w-4 text-atlas-muted" aria-hidden="true" />
          {modes.map((item) => (
            <button
              key={item}
              type="button"
              className={`h-7 rounded-md border px-2 text-xs transition ${selectedClass(item === selectedMode)}`}
              disabled={item === "Live"}
              title={item === "Live" ? "Live mode is locked until production controls are configured." : undefined}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2 rounded-md border border-atlas-line bg-white/[0.02] px-3 py-2 text-xs text-atlas-muted">
          <span className="font-mono text-atlas-text">{context.selectedSymbol}</span>
          <span>Confidence: {confidence}</span>
          <span className="flex items-center gap-1">
            <ShieldAlert className="h-3.5 w-3.5 text-atlas-amber" aria-hidden="true" />
            <RiskStateDot state={context.portfolioSummary.riskState} />
            {context.portfolioSummary.riskState}
          </span>
        </div>
      </div>
    </section>
  );
}
