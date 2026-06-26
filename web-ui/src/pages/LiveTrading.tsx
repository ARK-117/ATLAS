import { Hammer, LockKeyhole, ShieldAlert } from "lucide-react";
import { RiskBadge } from "../components/RiskBadge";
import { TradeTicket } from "../components/TradeTicket";

export function LiveTrading() {
  return (
    <div className="space-y-5">
      <section className="rounded-md border border-atlas-red/50 bg-atlas-red/10 p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <LockKeyhole className="h-6 w-6 text-atlas-red" aria-hidden="true" />
            <div>
              <p className="text-xs uppercase text-atlas-red">Live Mode Locked</p>
              <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Real Money Requires Production Approval</h1>
            </div>
          </div>
          <RiskBadge state="blocked" label="Execution disabled" />
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
        <TradeTicket mode="live" locked />

        <div className="atlas-panel p-5">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 text-atlas-amber" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Live Order Flow Gate</h2>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {[
              "Broker connection configured",
              "Secrets manager enabled",
              "User authenticated",
              "Risk policy approved",
              "Human approval workflow active",
              "Audit log writable",
              "Reconciliation service healthy",
              "Emergency shutdown tested"
            ].map((item, index) => (
              <div key={item} className="flex items-center justify-between rounded-md border border-atlas-line bg-white/[0.03] p-3">
                <span className="text-sm text-atlas-muted">{item}</span>
                <RiskBadge state={index === 5 ? "normal" : "blocked"} label={index === 5 ? "Ready" : "Locked"} />
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="atlas-panel p-5">
        <div className="flex items-start gap-3">
          <Hammer className="mt-0.5 h-5 w-5 text-atlas-amber" aria-hidden="true" />
          <div>
            <h2 className="text-lg font-semibold text-atlas-text">Desktop Packaging Status</h2>
            <p className="mt-2 text-sm leading-6 text-atlas-muted">
              The web UI builds successfully. Native Tauri packaging requires the Microsoft Visual C++ Build Tools linker
              before Windows installer generation can complete.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
