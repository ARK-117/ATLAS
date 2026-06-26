import { LockKeyhole, Send, ShieldAlert } from "lucide-react";

interface TradeTicketProps {
  mode: "paper" | "live";
  locked?: boolean;
}

export function TradeTicket({ mode, locked = false }: TradeTicketProps) {
  const disabled = locked || mode === "live";

  return (
    <section className="atlas-panel p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-atlas-text">{mode === "paper" ? "Paper Trade Ticket" : "Live Order Intent"}</h3>
          <p className="mt-1 text-xs text-atlas-muted">
            {mode === "paper" ? "Simulation flow with risk preview" : "Real-money execution remains locked"}
          </p>
        </div>
        {disabled ? <LockKeyhole className="h-5 w-5 text-atlas-red" aria-hidden="true" /> : <Send className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <label className="space-y-1 text-xs text-atlas-muted">
          Symbol
          <input className="atlas-input" defaultValue="NVDA" disabled={disabled} />
        </label>
        <label className="space-y-1 text-xs text-atlas-muted">
          Side
          <select className="atlas-input" disabled={disabled} defaultValue="buy">
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
        </label>
        <label className="space-y-1 text-xs text-atlas-muted">
          Quantity
          <input className="atlas-input" defaultValue="1" disabled={disabled} />
        </label>
        <label className="space-y-1 text-xs text-atlas-muted">
          Stop-loss
          <input className="atlas-input" defaultValue="118.00" disabled={disabled} />
        </label>
      </div>

      <div className="mt-4 rounded-md border border-atlas-amber/30 bg-atlas-amber/10 p-3 text-sm text-atlas-text">
        <div className="flex items-center gap-2 text-atlas-amber">
          <ShieldAlert className="h-4 w-4" aria-hidden="true" />
          <span className="text-xs uppercase">Risk preview</span>
        </div>
        <p className="mt-2 text-atlas-muted">
          Estimated notional, expected loss, liquidity, event risk, and approval status will be checked by the backend risk engine before submission.
        </p>
      </div>

      <button className="atlas-button mt-4 w-full justify-center" type="button" disabled={disabled}>
        {disabled ? "Locked" : "Run risk check"}
      </button>
    </section>
  );
}
