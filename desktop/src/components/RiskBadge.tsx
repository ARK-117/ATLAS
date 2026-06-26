import type { RiskState } from "../types";

interface RiskBadgeProps {
  state: RiskState;
  label?: string;
}

const riskStyles: Record<RiskState, string> = {
  normal: "border-atlas-green/40 bg-atlas-green/10 text-atlas-green",
  caution: "border-atlas-amber/40 bg-atlas-amber/10 text-atlas-amber",
  high: "border-orange-400/40 bg-orange-400/10 text-orange-300",
  blocked: "border-atlas-red/40 bg-atlas-red/10 text-atlas-red",
  emergency: "border-red-300/60 bg-red-500/20 text-red-200"
};

export function RiskBadge({ state, label }: RiskBadgeProps) {
  const text = label ?? state.charAt(0).toUpperCase() + state.slice(1);

  return (
    <span className={`inline-flex h-7 items-center rounded-md border px-2.5 text-xs font-semibold ${riskStyles[state]}`}>
      {text}
    </span>
  );
}
