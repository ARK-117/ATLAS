import { FlaskConical, LineChart } from "lucide-react";
import { RiskBadge } from "../components/RiskBadge";
import { Sparkline } from "../components/Sparkline";
import { sparklinePoints } from "../data/mockData";

export function BacktestingLab() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs uppercase text-atlas-cyan">Strategy Lab</p>
        <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Backtesting</h1>
      </div>

      <section className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="atlas-panel p-5">
          <div className="flex items-center gap-3">
            <FlaskConical className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Strategy Builder</h2>
          </div>
          <div className="mt-5 space-y-3">
            {["Asset selector", "Entry rules", "Exit rules", "Stop-loss", "Fees", "Slippage"].map((item) => (
              <label key={item} className="block text-xs text-atlas-muted">
                {item}
                <input className="atlas-input mt-1" defaultValue={item === "Asset selector" ? "NVDA, MSFT, AMD" : ""} />
              </label>
            ))}
          </div>
          <button className="atlas-button mt-4 w-full justify-center" type="button">
            Run test
          </button>
        </aside>

        <div className="space-y-5">
          <section className="atlas-panel p-5">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <LineChart className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
                <h2 className="text-lg font-semibold text-atlas-text">Equity Curve</h2>
              </div>
              <RiskBadge state="caution" label="Bias checks required" />
            </div>
            <div className="mt-5 h-[300px] rounded-md border border-atlas-line bg-atlas-void p-5">
              <Sparkline points={sparklinePoints} direction="up" />
            </div>
          </section>
          <section className="grid gap-3 md:grid-cols-4">
            {["Return 0.0%", "Max DD 0.0%", "Sharpe n/a", "Trades 0"].map((metric) => (
              <div key={metric} className="atlas-panel p-4 font-mono text-atlas-text">{metric}</div>
            ))}
          </section>
        </div>
      </section>
    </div>
  );
}
