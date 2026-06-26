import { PauseCircle, ShieldAlert, SlidersHorizontal } from "lucide-react";
import { RiskBadge } from "../components/RiskBadge";
import { riskControls } from "../data/mockData";

export function RiskCenter() {
  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-cyan">Safety Layer</p>
          <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Risk Center</h1>
        </div>
        <button className="atlas-danger-button" type="button">
          <PauseCircle className="h-4 w-4" aria-hidden="true" />
          Pause New Trades
        </button>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {riskControls.map((control) => (
          <article key={control.label} className="atlas-panel p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase text-atlas-muted">{control.label}</p>
                <p className="mt-2 font-mono text-2xl font-semibold text-atlas-text">{control.value}</p>
              </div>
              <RiskBadge state={control.state} />
            </div>
          </article>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="atlas-panel p-5">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 text-atlas-amber" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Risk Dashboard</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {[
              "Daily loss limit",
              "Max drawdown",
              "Position concentration",
              "Sector concentration",
              "Liquidity risk",
              "Earnings risk",
              "Data quality risk",
              "Broker status"
            ].map((item, index) => (
              <div key={item} className="flex items-center justify-between rounded-md border border-atlas-line bg-white/[0.03] p-3">
                <span className="text-sm text-atlas-muted">{item}</span>
                <RiskBadge state={index > 5 ? "blocked" : index > 2 ? "caution" : "normal"} />
              </div>
            ))}
          </div>
        </div>

        <aside className="atlas-panel p-5">
          <div className="flex items-center gap-3">
            <SlidersHorizontal className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Control Surface</h2>
          </div>
          <div className="mt-5 space-y-4">
            {["Max trade size", "Max portfolio exposure", "Max leverage", "Max margin usage"].map((item, index) => (
              <label key={item} className="block text-sm text-atlas-muted">
                <span className="flex justify-between">
                  <span>{item}</span>
                  <span className="font-mono">{index === 0 ? "$1,000" : index === 2 ? "1.0x" : "0%"}</span>
                </span>
                <input className="mt-2 h-2 w-full accent-atlas-cyan" type="range" min="0" max="100" defaultValue={index === 0 ? 15 : 0} />
              </label>
            ))}
          </div>
        </aside>
      </section>
    </div>
  );
}
