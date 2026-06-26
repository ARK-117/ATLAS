interface StatusPillProps {
  label: string;
  value: string;
  tone?: "neutral" | "good" | "warning" | "danger" | "info";
}

const toneClasses = {
  neutral: "border-atlas-line bg-white/5 text-atlas-muted",
  good: "border-atlas-green/40 bg-atlas-green/10 text-atlas-green",
  warning: "border-atlas-amber/40 bg-atlas-amber/10 text-atlas-amber",
  danger: "border-atlas-red/40 bg-atlas-red/10 text-atlas-red",
  info: "border-atlas-cyan/40 bg-atlas-cyan/10 text-atlas-cyan"
};

export function StatusPill({ label, value, tone = "neutral" }: StatusPillProps) {
  return (
    <div className={`flex h-8 items-center gap-2 rounded-md border px-3 text-xs ${toneClasses[tone]}`}>
      <span className="text-atlas-muted">{label}</span>
      <span className="font-semibold text-atlas-text">{value}</span>
    </div>
  );
}
