import { BrainCircuit } from "lucide-react";
import { AIChat } from "../components/ai/AIChat";
import type { AppContext, AssistantAction, AssistantMessage, ToolActivity } from "../types";

interface RightAIPanelProps {
  context: AppContext;
  messages: AssistantMessage[];
  activities: ToolActivity[];
  action?: AssistantAction;
  onSend: (message: string) => void;
}

export function RightAIPanel({ context, messages, activities, action, onSend }: RightAIPanelProps) {
  return (
    <aside className="col-start-3 row-start-2 row-end-3 hidden h-full border-l border-atlas-line bg-atlas-deck xl:flex xl:flex-col">
      <div className="border-b border-atlas-line p-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-atlas-text">ATLAS Assistant</h2>
            <p className="mt-1 text-xs text-atlas-muted">Natural chat, context, and tool activity</p>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-md border border-atlas-line bg-white/[0.03]">
            <BrainCircuit className="h-5 w-5 text-atlas-blue" aria-hidden="true" />
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 p-4">
        <AIChat
          compact
          context={context}
          messages={messages}
          activities={activities}
          action={action}
          onSend={onSend}
        />
      </div>
    </aside>
  );
}
