import { Clock, Power, Radio, ShieldAlert, Zap } from "lucide-react";
import { systemStatus } from "../data/mockData";
import { StatusPill } from "../components/StatusPill";

export function TopStatusBar() {
  return (
    <header className="col-start-2 col-end-3 row-start-1 flex h-16 min-w-0 items-center justify-between gap-3 border-b border-atlas-line bg-atlas-deck px-5 xl:col-end-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="min-w-[168px]">
          <div className="text-sm font-semibold text-atlas-text">ATLAS</div>
          <div className="truncate text-xs text-atlas-muted">Automated Trading, Learning, and Analysis System</div>
        </div>
        <StatusPill label="Mode" value={systemStatus.mode} tone="info" />
        <div className="hidden 2xl:block">
          <StatusPill label="Broker" value={systemStatus.broker} tone="warning" />
        </div>
        <div className="hidden 2xl:block">
          <StatusPill label="Market" value={systemStatus.market} tone="neutral" />
        </div>
      </div>

      <div className="flex min-w-0 items-center justify-end gap-2">
        <div className="hidden xl:block">
          <StatusPill label="Data" value={systemStatus.dataFreshness} tone="neutral" />
        </div>
        <div className="hidden 2xl:block">
          <StatusPill label="AI" value={systemStatus.ai} tone="warning" />
        </div>
        <StatusPill label="Risk" value={systemStatus.risk} tone="good" />
        <button type="button" className="atlas-danger-button">
          <Power className="h-4 w-4" aria-hidden="true" />
          Kill Switch
        </button>
        <div className="flex h-8 items-center gap-2 rounded-md border border-atlas-line bg-white/5 px-3 text-xs text-atlas-muted">
          <Clock className="h-4 w-4" aria-hidden="true" />
          UTC
        </div>
        <Radio className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
        <ShieldAlert className="h-4 w-4 text-atlas-amber" aria-hidden="true" />
        <Zap className="h-4 w-4 text-atlas-green" aria-hidden="true" />
      </div>
    </header>
  );
}
