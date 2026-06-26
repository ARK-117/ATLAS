import { PieChart, Wallet } from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { commandMetrics, portfolioPositions } from "../data/mockData";

export function Portfolio() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs uppercase text-atlas-cyan">Portfolio Intelligence</p>
        <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Portfolio</h1>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {commandMetrics.slice(0, 4).map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="atlas-panel overflow-hidden">
          <table className="w-full table-fixed text-left text-sm">
            <thead className="border-b border-atlas-line bg-white/[0.03] text-xs uppercase text-atlas-muted">
              <tr>
                <th className="px-4 py-3">Asset</th>
                <th className="px-4 py-3">Quantity</th>
                <th className="px-4 py-3">Avg</th>
                <th className="px-4 py-3">Price</th>
                <th className="px-4 py-3">Value</th>
                <th className="px-4 py-3">P/L</th>
                <th className="px-4 py-3">Weight</th>
              </tr>
            </thead>
            <tbody>
              {portfolioPositions.map((position) => (
                <tr key={position.asset} className="border-b border-atlas-line/70">
                  <td className="px-4 py-3 font-semibold text-atlas-text">{position.asset}</td>
                  <td className="px-4 py-3 font-mono text-atlas-muted">{position.quantity}</td>
                  <td className="px-4 py-3 font-mono text-atlas-muted">{position.avg}</td>
                  <td className="px-4 py-3 font-mono text-atlas-text">{position.price}</td>
                  <td className="px-4 py-3 font-mono text-atlas-text">{position.value}</td>
                  <td className="px-4 py-3 font-mono text-atlas-green">{position.pnl}</td>
                  <td className="px-4 py-3 font-mono text-atlas-muted">{position.weight}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <aside className="space-y-5">
          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <PieChart className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">Allocation</h2>
            </div>
            <div className="mt-5 space-y-3">
              {["Cash 100%", "Equities 0%", "ETFs 0%", "High-risk products 0%"].map((row) => (
                <div key={row}>
                  <div className="mb-1 text-sm text-atlas-muted">{row}</div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div className="h-2 rounded-full bg-atlas-cyan" style={{ width: row.startsWith("Cash") ? "100%" : "0%" }} />
                  </div>
                </div>
              ))}
            </div>
          </section>
          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <Wallet className="h-5 w-5 text-atlas-green" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">AI Portfolio Review</h2>
            </div>
            <p className="mt-4 text-sm leading-6 text-atlas-muted">
              The portfolio is currently cash-only in the preview. Future backend data will calculate concentration, correlation, drawdown, liquidity, and scenario impact.
            </p>
          </section>
        </aside>
      </section>
    </div>
  );
}
