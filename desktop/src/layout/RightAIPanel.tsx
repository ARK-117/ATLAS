import { BrainCircuit, Search, ShieldAlert, Sparkles } from "lucide-react";
import { AgentActivityFeed } from "../components/AgentActivityFeed";
import { RiskBadge } from "../components/RiskBadge";
import { agents } from "../data/mockData";

export function RightAIPanel() {
  return (
    <aside className="col-start-3 row-start-2 row-end-3 hidden h-full border-l border-atlas-line bg-atlas-deck xl:flex xl:flex-col">
      <div className="border-b border-atlas-line p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-atlas-text">AI Intelligence</h2>
            <p className="mt-1 text-xs text-atlas-muted">Research, risk, and agent context</p>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-md border border-atlas-cyan/30 bg-atlas-cyan/10">
            <BrainCircuit className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <section className="atlas-panel p-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold text-atlas-text">Current Context</h3>
            <RiskBadge state="normal" label="Research" />
          </div>
          <p className="mt-3 text-sm leading-6 text-atlas-muted">
            Live execution is locked. ATLAS can research, explain, simulate, and prepare order intents only after backend risk checks are connected.
          </p>
        </section>

        <section className="atlas-panel p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-atlas-text">
            <Sparkles className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
            Signal Brief
          </div>
          <div className="space-y-3 text-sm text-atlas-muted">
            <p>AI infrastructure remains the strongest watched theme.</p>
            <p>High-volatility names need tighter sizing and event checks.</p>
            <p>Broker status is unknown, so live routes stay disabled.</p>
          </div>
        </section>

        <section className="atlas-panel p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-atlas-text">
            <ShieldAlert className="h-4 w-4 text-atlas-amber" aria-hidden="true" />
            Risk Warnings
          </div>
          <div className="space-y-2">
            <RiskBadge state="blocked" label="Live orders blocked" />
            <RiskBadge state="caution" label="Data preview" />
            <RiskBadge state="normal" label="Audit enabled" />
          </div>
        </section>

        <section className="atlas-panel p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-atlas-text">
            <Search className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
            Agent Activity
          </div>
          <AgentActivityFeed agents={agents} />
        </section>
      </div>
    </aside>
  );
}
