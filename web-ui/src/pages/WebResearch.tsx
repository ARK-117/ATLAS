import { Globe2, Search } from "lucide-react";
import { SourceCard } from "../components/ai/SourceCard";
import { AIInput } from "../components/ai/AIInput";
import type { AppContext } from "../types";

interface WebResearchProps {
  context: AppContext;
  onSend: (message: string) => void;
}

export function WebResearch({ context, onSend }: WebResearchProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-blue">Source-Grounded Research</p>
          <h1 className="mt-1 text-2xl font-semibold text-atlas-text">Web Research</h1>
        </div>
        <div className="rounded-md border border-atlas-line bg-white/[0.03] px-3 py-2 text-sm text-atlas-muted">
          Selected asset: <span className="font-mono text-atlas-text">{context.selectedSymbol}</span>
        </div>
      </div>

      <section className="atlas-panel p-4">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-atlas-text">
          <Search className="h-4 w-4 text-atlas-blue" aria-hidden="true" />
          Ask ATLAS to research the web
        </div>
        <AIInput
          placeholder="Example: find recent news about Nvidia AI chips"
          onSend={(message) => onSend(`web research: ${message}`)}
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="atlas-panel p-4">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-atlas-text">
            <Globe2 className="h-4 w-4 text-atlas-blue" aria-hidden="true" />
            Source Workspace
          </div>
          <div className="grid gap-3">
            <SourceCard
              title="Web search"
              status="not-connected"
              description="Will search current public sources through the backend web tool. ATLAS will not invent current results."
            />
            <SourceCard
              title="Fetch webpage"
              status="not-connected"
              description="Will fetch and extract article content, title, date, author, and relevant facts."
            />
            <SourceCard
              title="Contradiction check"
              status="not-connected"
              description="Will compare source claims and warn when sources disagree or are low confidence."
            />
          </div>
        </div>

        <aside className="atlas-panel p-4">
          <h2 className="text-sm font-semibold text-atlas-text">Research Rules</h2>
          <div className="mt-3 space-y-3 text-sm leading-6 text-atlas-muted">
            <p>Current facts require backend web tools and source cards.</p>
            <p>ATLAS must cite or summarize sources when web research is used.</p>
            <p>When the fetch tool fails, ATLAS should say so instead of guessing.</p>
          </div>
        </aside>
      </section>
    </div>
  );
}
