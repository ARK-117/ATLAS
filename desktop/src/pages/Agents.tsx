import { Bot, Network } from "lucide-react";
import { AgentActivityFeed } from "../components/AgentActivityFeed";
import { agents } from "../data/mockData";

export function Agents() {
  const allAgents = [
    ...agents,
    { agent: "Technical Agent", status: "Ready", task: "Momentum and volatility scoring", confidence: 81 },
    { agent: "Fundamental Agent", status: "Ready", task: "Filings and earnings synthesis", confidence: 79 },
    { agent: "Portfolio Agent", status: "Waiting", task: "Portfolio backend not connected", confidence: 67 }
  ];

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs uppercase text-atlas-cyan">Agent System</p>
        <h1 className="mt-1 text-3xl font-semibold text-atlas-text">AI Agents</h1>
      </div>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="grid gap-4 md:grid-cols-2">
          {allAgents.map((agent) => (
            <article key={agent.agent} className="atlas-panel p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-md border border-atlas-cyan/30 bg-atlas-cyan/10">
                    <Bot className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-atlas-text">{agent.agent}</h3>
                    <p className="mt-1 text-sm text-atlas-muted">{agent.task}</p>
                  </div>
                </div>
                <span className="font-mono text-sm text-atlas-cyan">{agent.confidence}%</span>
              </div>
            </article>
          ))}
        </div>

        <aside className="atlas-panel p-5">
          <div className="mb-4 flex items-center gap-3">
            <Network className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Activity Timeline</h2>
          </div>
          <AgentActivityFeed agents={allAgents.slice(0, 5)} />
        </aside>
      </section>
    </div>
  );
}
