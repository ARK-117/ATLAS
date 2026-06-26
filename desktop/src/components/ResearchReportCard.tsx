import { FileSearch } from "lucide-react";
import type { RiskState } from "../types";
import { RiskBadge } from "./RiskBadge";

interface ResearchReportCardProps {
  report: {
    title: string;
    confidence: number;
    risk: RiskState;
    summary: string;
    bull: string;
    bear: string;
  };
}

export function ResearchReportCard({ report }: ResearchReportCardProps) {
  return (
    <article className="atlas-panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md border border-atlas-cyan/30 bg-atlas-cyan/10">
            <FileSearch className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-atlas-text">{report.title}</h3>
            <p className="mt-1 text-xs text-atlas-muted">Confidence {report.confidence}%</p>
          </div>
        </div>
        <RiskBadge state={report.risk} />
      </div>
      <p className="mt-4 text-sm leading-6 text-atlas-muted">{report.summary}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-md border border-atlas-green/30 bg-atlas-green/10 p-3 text-sm text-atlas-text">
          <span className="block text-xs uppercase text-atlas-green">Bull case</span>
          {report.bull}
        </div>
        <div className="rounded-md border border-atlas-red/30 bg-atlas-red/10 p-3 text-sm text-atlas-text">
          <span className="block text-xs uppercase text-atlas-red">Bear case</span>
          {report.bear}
        </div>
      </div>
    </article>
  );
}
