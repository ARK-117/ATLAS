import { Database, LockKeyhole, Settings as SettingsIcon, SlidersHorizontal } from "lucide-react";
import { RiskBadge } from "../components/RiskBadge";

export function Settings() {
  const sections = [
    { title: "General", icon: SettingsIcon, values: ["Theme: ATLAS dark", "Startup view: Command Center", "Timezone: system"] },
    { title: "AI", icon: SlidersHorizontal, values: ["Local model: Ollama", "Temperature: controlled", "Memory: permissioned"] },
    { title: "Market Data", icon: Database, values: ["Provider: not configured", "Refresh: manual", "Quality checks: required"] },
    { title: "Security", icon: LockKeyhole, values: ["Secrets: external manager required", "Session lock: planned", "Audit: append-only"] }
  ];

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs uppercase text-atlas-cyan">Configuration</p>
        <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Settings</h1>
      </div>

      <section className="grid gap-5 md:grid-cols-2">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <article key={section.title} className="atlas-panel p-5">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
                  <h2 className="text-lg font-semibold text-atlas-text">{section.title}</h2>
                </div>
                <RiskBadge state={section.title === "Security" ? "caution" : "normal"} />
              </div>
              <div className="mt-4 space-y-3">
                {section.values.map((value) => (
                  <div key={value} className="rounded-md border border-atlas-line bg-white/[0.03] p-3 text-sm text-atlas-muted">
                    {value}
                  </div>
                ))}
              </div>
            </article>
          );
        })}
      </section>
    </div>
  );
}
