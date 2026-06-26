import { BrainCircuit } from "lucide-react";
import { AIChat } from "../components/ai/AIChat";
import type { AppContext, AssistantAction, AssistantMessage, ToolActivity } from "../types";

interface AIChatPageProps {
  context: AppContext;
  messages: AssistantMessage[];
  activities: ToolActivity[];
  action?: AssistantAction;
  onSend: (message: string) => void;
}

export function AIChatPage({ context, messages, activities, action, onSend }: AIChatPageProps) {
  return (
    <div className="flex h-full flex-col gap-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-atlas-blue">Natural Assistant</p>
          <h1 className="mt-1 text-2xl font-semibold text-atlas-text">AI Chat</h1>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-atlas-line bg-white/[0.03] px-3 py-2 text-sm text-atlas-muted">
          <BrainCircuit className="h-4 w-4 text-atlas-blue" aria-hidden="true" />
          Uses current app context
        </div>
      </div>

      <section className="min-h-0 flex-1">
        <AIChat context={context} messages={messages} activities={activities} action={action} onSend={onSend} />
      </section>
    </div>
  );
}
