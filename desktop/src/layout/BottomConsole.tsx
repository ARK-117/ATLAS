import { Terminal } from "lucide-react";
import { auditEvents } from "../data/mockData";
import { RiskBadge } from "../components/RiskBadge";

export function BottomConsole() {
  return (
    <footer className="col-start-2 col-end-3 row-start-3 h-[132px] border-t border-atlas-line bg-atlas-deck xl:col-end-4">
      <div className="flex h-10 items-center gap-2 border-b border-atlas-line px-4 text-sm font-semibold text-atlas-text">
        <Terminal className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
        Event Console
      </div>
      <div className="grid h-[92px] grid-cols-4 gap-3 overflow-hidden p-3">
        {auditEvents.map((event) => (
          <div key={`${event.time}-${event.subject}`} className="rounded-md border border-atlas-line bg-white/[0.03] p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="font-mono text-xs text-atlas-muted">{event.time}</span>
              <RiskBadge state={event.risk} />
            </div>
            <p className="mt-2 truncate text-sm text-atlas-text">{event.subject}</p>
          </div>
        ))}
      </div>
    </footer>
  );
}
