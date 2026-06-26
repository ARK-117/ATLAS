import { Bot, CheckCircle2, Clock, ShieldAlert } from "lucide-react";
import type { AgentActivity } from "../types";

interface AgentActivityFeedProps {
  agents: AgentActivity[];
}

export function AgentActivityFeed({ agents }: AgentActivityFeedProps) {
  return (
    <div className="space-y-3">
      {agents.map((agent) => {
        const Icon = agent.warning ? ShieldAlert : agent.status === "Ready" ? CheckCircle2 : Clock;
        return (
          <article key={agent.agent} className="flex gap-3 rounded-md border border-atlas-line bg-white/[0.03] p-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-atlas-cyan/30 bg-atlas-cyan/10">
              <Bot className="h-4 w-4 text-atlas-cyan" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <h4 className="truncate text-sm font-semibold text-atlas-text">{agent.agent}</h4>
                <Icon className="h-4 w-4 text-atlas-amber" aria-hidden="true" />
              </div>
              <p className="mt-1 text-xs text-atlas-muted">{agent.task}</p>
              <div className="mt-2 h-1.5 rounded-full bg-white/10">
                <div className="h-1.5 rounded-full bg-atlas-cyan" style={{ width: `${agent.confidence}%` }} />
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
