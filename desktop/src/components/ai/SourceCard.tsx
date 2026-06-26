interface SourceCardProps {
  title: string;
  description: string;
  status: "ready" | "not-connected";
}

export function SourceCard({ title, description, status }: SourceCardProps) {
  return (
    <article className="rounded-md border border-atlas-line bg-white/[0.03] p-3">
      <div className="flex items-center justify-between gap-3">
        <h4 className="text-sm font-semibold text-atlas-text">{title}</h4>
        <span className="text-xs text-atlas-muted">{status === "ready" ? "Ready" : "Not connected"}</span>
      </div>
      <p className="mt-2 text-sm leading-5 text-atlas-muted">{description}</p>
    </article>
  );
}
