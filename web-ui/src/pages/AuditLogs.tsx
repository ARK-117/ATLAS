import { Download, FileText, Search } from "lucide-react";
import { AuditTimeline } from "../components/AuditTimeline";
import { auditEvents } from "../data/mockData";

export function AuditLogs() {
  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-cyan">Accountability</p>
          <h1 className="mt-1 text-3xl font-semibold text-atlas-text">Audit Logs</h1>
        </div>
        <button className="atlas-button" type="button">
          <Download className="h-4 w-4" aria-hidden="true" />
          Export
        </button>
      </div>

      <section className="atlas-panel flex flex-wrap items-center gap-3 p-4">
        <div className="flex h-10 min-w-[280px] items-center gap-2 rounded-md border border-atlas-line bg-atlas-void px-3">
          <Search className="h-4 w-4 text-atlas-muted" aria-hidden="true" />
          <input className="w-full bg-transparent text-sm text-atlas-text outline-none" placeholder="Filter audit events" />
        </div>
        {["Research", "Risk", "Order intent", "Approval", "System", "Errors"].map((filter) => (
          <button key={filter} type="button" className="atlas-chip">
            {filter}
          </button>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="atlas-panel p-5">
          <div className="mb-4 flex items-center gap-3">
            <FileText className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-atlas-text">Timeline</h2>
          </div>
          <AuditTimeline events={auditEvents} />
        </aside>

        <div className="atlas-panel overflow-hidden">
          <table className="w-full table-fixed text-left text-sm">
            <thead className="border-b border-atlas-line bg-white/[0.03] text-xs uppercase text-atlas-muted">
              <tr>
                <th className="w-28 px-4 py-3">Time</th>
                <th className="w-32 px-4 py-3">Type</th>
                <th className="px-4 py-3">Subject</th>
                <th className="w-48 px-4 py-3">Result</th>
              </tr>
            </thead>
            <tbody>
              {auditEvents.map((event) => (
                <tr key={`${event.time}-${event.subject}`} className="border-b border-atlas-line/70">
                  <td className="px-4 py-3 font-mono text-atlas-muted">{event.time}</td>
                  <td className="px-4 py-3 text-atlas-cyan">{event.type}</td>
                  <td className="px-4 py-3 text-atlas-text">{event.subject}</td>
                  <td className="px-4 py-3 text-atlas-muted">{event.result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
