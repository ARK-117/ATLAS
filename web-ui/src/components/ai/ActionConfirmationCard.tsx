import type { AssistantAction } from "../../types";
import { RiskBadge } from "../RiskBadge";

interface ActionConfirmationCardProps {
  action: AssistantAction;
}

export function ActionConfirmationCard({ action }: ActionConfirmationCardProps) {
  return (
    <article className="rounded-md border border-atlas-line bg-atlas-panelSoft p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="text-sm font-semibold text-atlas-text">{action.title}</h4>
          <p className="mt-2 text-sm leading-5 text-atlas-muted">{action.description}</p>
        </div>
        <RiskBadge state={action.risk} />
      </div>
      <div className="mt-4 flex gap-2">
        <button className="atlas-button" type="button">
          {action.confirmLabel}
        </button>
        <button className="atlas-chip" type="button">
          {action.cancelLabel}
        </button>
        <button className="atlas-chip" type="button">
          Edit details
        </button>
      </div>
    </article>
  );
}
