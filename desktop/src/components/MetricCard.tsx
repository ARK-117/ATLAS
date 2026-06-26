import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import type { Metric } from "../types";

interface MetricCardProps {
  metric: Metric;
}

export function MetricCard({ metric }: MetricCardProps) {
  const Icon = metric.trend === "up" ? ArrowUpRight : metric.trend === "down" ? ArrowDownRight : ArrowRight;
  const tone = metric.trend === "up" ? "text-atlas-green" : metric.trend === "down" ? "text-atlas-red" : "text-atlas-cyan";

  return (
    <section className="atlas-panel flex min-h-[126px] flex-col justify-between p-4">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs uppercase text-atlas-muted">{metric.label}</p>
        <Icon className={`h-4 w-4 ${tone}`} aria-hidden="true" />
      </div>
      <div>
        <div className="font-mono text-2xl font-semibold text-atlas-text">{metric.value}</div>
        <p className="mt-1 text-sm text-atlas-muted">{metric.detail}</p>
      </div>
    </section>
  );
}
