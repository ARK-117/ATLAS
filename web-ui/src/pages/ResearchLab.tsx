import { Bot, Microscope, Search } from "lucide-react";
import { AgentActivityFeed } from "../components/AgentActivityFeed";
import { ResearchReportCard } from "../components/ResearchReportCard";
import { agents, researchReports } from "../data/mockData";

export function ResearchLab() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs uppercase text-atlas-cyan">AI Research System</p>
        <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Research Lab</h1>
      </div>

      <section className="atlas-panel p-5">
        <div className="flex gap-3">
          <div className="flex min-h-12 flex-1 items-center gap-3 rounded-md border border-atlas-line bg-atlas-void px-4">
            <Search className="h-5 w-5 text-atlas-muted" aria-hidden="true" />
            <input
              className="w-full bg-transparent text-sm text-atlas-text outline-none"
              defaultValue="Compare NVDA, MSFT, and AMD for risk-adjusted AI exposure"
            />
          </div>
          <button className="atlas-button px-5" type="button">
            <Microscope className="h-4 w-4" aria-hidden="true" />
            Research
          </button>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {[
            "Quick summary",
            "Deep research",
            "Bull vs bear",
            "Risk-first",
            "Technical",
            "Fundamental",
            "Portfolio impact"
          ].map((mode) => (
            <button key={mode} type="button" className="atlas-chip">
              {mode}
            </button>
          ))}
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4">
          {researchReports.map((report) => (
            <ResearchReportCard key={report.title} report={report} />
          ))}
        </div>
        <aside className="atlas-panel p-5">
          <div className="mb-4 flex items-center gap-3">
            <Bot className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Agent Debate</h2>
          </div>
          <AgentActivityFeed agents={agents} />
        </aside>
      </section>
    </div>
  );
}
