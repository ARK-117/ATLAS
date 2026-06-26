import { FileText } from "lucide-react";
import type { AuditEvent } from "../types";
import { RiskBadge } from "./RiskBadge";

interface AuditTimelineProps {
  events: AuditEvent[];
}

export function AuditTimeline({ events }: AuditTimelineProps) {
  return (
    <div className="space-y-3">
      {events.map((event) => (
        <article key={`${event.time}-${event.subject}`} className="flex gap-3 rounded-md border border-atlas-line bg-white/[0.03] p-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-atlas-line bg-atlas-panel">
            <FileText className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-2">
              <p className="font-mono text-xs text-atlas-muted">{event.time}</p>
              <RiskBadge state={event.risk} />
            </div>
            <p className="mt-1 text-sm font-semibold text-atlas-text">{event.subject}</p>
            <p className="text-xs text-atlas-muted">{event.type} - {event.result}</p>
          </div>
        </article>
      ))}
    </div>
  );
}
