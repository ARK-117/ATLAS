import { Plus, Search } from "lucide-react";
import { RiskBadge } from "../components/RiskBadge";
import { watchlistRows } from "../data/mockData";

interface WatchlistProps {
  onSelectAsset: (symbol: string) => void;
}

export function Watchlist({ onSelectAsset }: WatchlistProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-cyan">Asset Monitor</p>
          <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Watchlist</h1>
        </div>
        <button className="atlas-button" type="button">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Add Symbol
        </button>
      </div>

      <section className="atlas-panel flex flex-wrap items-center gap-3 p-4">
        <div className="flex h-10 min-w-[260px] items-center gap-2 rounded-md border border-atlas-line bg-atlas-void px-3">
          <Search className="h-4 w-4 text-atlas-muted" aria-hidden="true" />
          <input className="w-full bg-transparent text-sm text-atlas-text outline-none" placeholder="Filter assets" />
        </div>
        {["Stocks", "ETFs", "High AI score", "High risk", "Earnings soon", "Breakout"].map((filter) => (
          <button key={filter} type="button" className="atlas-chip">
            {filter}
          </button>
        ))}
      </section>

      <section className="atlas-panel overflow-hidden">
        <table className="w-full table-fixed text-left text-sm">
          <thead className="border-b border-atlas-line bg-white/[0.03] text-xs uppercase text-atlas-muted">
            <tr>
              <th className="w-24 px-4 py-3">Symbol</th>
              <th className="px-4 py-3">Asset</th>
              <th className="w-28 px-4 py-3">Price</th>
              <th className="w-24 px-4 py-3">Change</th>
              <th className="w-24 px-4 py-3">Volume</th>
              <th className="w-24 px-4 py-3">AI</th>
              <th className="w-28 px-4 py-3">Risk</th>
              <th className="w-32 px-4 py-3">Last</th>
            </tr>
          </thead>
          <tbody>
            {watchlistRows.map((row) => (
              <tr key={row.symbol} className="border-b border-atlas-line/70 hover:bg-white/[0.03]">
                <td className="px-4 py-3">
                  <button className="font-mono font-semibold text-atlas-cyan" type="button" onClick={() => onSelectAsset(row.symbol)}>
                    {row.symbol}
                  </button>
                </td>
                <td className="truncate px-4 py-3 text-atlas-text">{row.name}</td>
                <td className="px-4 py-3 font-mono text-atlas-text">{row.price}</td>
                <td className={row.direction === "down" ? "px-4 py-3 text-atlas-red" : "px-4 py-3 text-atlas-green"}>{row.change}</td>
                <td className="px-4 py-3 text-atlas-muted">{row.volume}</td>
                <td className="px-4 py-3 font-mono text-atlas-text">{row.aiScore}</td>
                <td className="px-4 py-3">
                  <RiskBadge state={row.riskScore > 70 ? "high" : row.riskScore > 50 ? "caution" : "normal"} label={`${row.riskScore}`} />
                </td>
                <td className="px-4 py-3 text-atlas-muted">{row.lastResearched}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
