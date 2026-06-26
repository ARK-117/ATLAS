import { ClipboardList, Wallet } from "lucide-react";
import { TradeTicket } from "../components/TradeTicket";
import { portfolioPositions } from "../data/mockData";

export function PaperTrading() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs uppercase text-atlas-cyan">Simulation</p>
        <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Paper Trading</h1>
      </div>

      <section className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
        <TradeTicket mode="paper" />

        <div className="space-y-5">
          <section className="atlas-panel p-5">
            <div className="flex items-center gap-3">
              <Wallet className="h-5 w-5 text-atlas-green" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">Simulated Account</h2>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-4">
              {["Cash $10,000", "Positions 0", "Daily P/L $0.00", "Risk Normal"].map((item) => (
                <div key={item} className="rounded-md border border-atlas-line bg-white/[0.03] p-3 text-sm text-atlas-muted">
                  {item}
                </div>
              ))}
            </div>
          </section>

          <section className="atlas-panel overflow-hidden">
            <div className="flex items-center gap-3 border-b border-atlas-line p-4">
              <ClipboardList className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-atlas-text">Paper Positions</h2>
            </div>
            <table className="w-full table-fixed text-left text-sm">
              <tbody>
                {portfolioPositions.map((position) => (
                  <tr key={position.asset} className="border-b border-atlas-line/70">
                    <td className="px-4 py-3 font-semibold text-atlas-text">{position.asset}</td>
                    <td className="px-4 py-3 font-mono text-atlas-muted">{position.quantity}</td>
                    <td className="px-4 py-3 font-mono text-atlas-text">{position.value}</td>
                    <td className="px-4 py-3 font-mono text-atlas-green">{position.pnl}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      </section>
    </div>
  );
}
