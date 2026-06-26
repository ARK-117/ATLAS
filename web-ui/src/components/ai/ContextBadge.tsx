import type { AppContext } from "../../types";

interface ContextBadgeProps {
  context: AppContext;
}

export function ContextBadge({ context }: ContextBadgeProps) {
  return (
    <div className="rounded-md border border-atlas-line bg-white/[0.03] p-3 text-xs text-atlas-muted">
      <div className="flex items-center justify-between gap-3">
        <span className="font-semibold text-atlas-text">Context</span>
        <span className="font-mono">{context.mode}</span>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-2">
        <span>View: {context.activeView}</span>
        <span>Asset: {context.selectedSymbol}</span>
        <span>Risk: {context.portfolioSummary.riskState}</span>
        <span>Tools: {context.availableTools.length}</span>
      </div>
    </div>
  );
}
