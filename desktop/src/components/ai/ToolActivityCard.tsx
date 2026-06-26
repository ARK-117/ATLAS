import { AlertTriangle, CheckCircle2, Clock, XCircle } from "lucide-react";
import type { ToolActivity } from "../../types";

interface ToolActivityCardProps {
  activity: ToolActivity;
}

const statusMeta = {
  pending: { icon: Clock, className: "text-atlas-amber", label: "Pending" },
  success: { icon: CheckCircle2, className: "text-atlas-green", label: "Success" },
  failed: { icon: XCircle, className: "text-atlas-red", label: "Failed" },
  blocked: { icon: AlertTriangle, className: "text-atlas-amber", label: "Blocked" }
};

export function ToolActivityCard({ activity }: ToolActivityCardProps) {
  const meta = statusMeta[activity.status];
  const Icon = meta.icon;

  return (
    <article className="rounded-md border border-atlas-line bg-white/[0.03] p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <Icon className={`h-4 w-4 ${meta.className}`} aria-hidden="true" />
            <h4 className="truncate font-mono text-xs font-semibold text-atlas-text">{activity.toolName}</h4>
          </div>
          <p className="mt-2 text-sm leading-5 text-atlas-muted">{activity.summary}</p>
        </div>
        <span className="shrink-0 font-mono text-xs text-atlas-muted">{activity.timestamp}</span>
      </div>
      {activity.details ? (
        <details className="mt-2 text-xs text-atlas-muted">
          <summary className="cursor-pointer text-atlas-text">Details</summary>
          <p className="mt-2 leading-5">{activity.details}</p>
        </details>
      ) : null}
    </article>
  );
}
