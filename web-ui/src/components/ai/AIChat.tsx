import type { AppContext, AssistantAction, AssistantMessage, ToolActivity } from "../../types";
import { ActionConfirmationCard } from "./ActionConfirmationCard";
import { AIInput } from "./AIInput";
import { AIMessage } from "./AIMessage";
import { ContextBadge } from "./ContextBadge";
import { SuggestedPrompts } from "./SuggestedPrompts";
import { ToolActivityCard } from "./ToolActivityCard";

interface AIChatProps {
  context: AppContext;
  messages: AssistantMessage[];
  activities: ToolActivity[];
  action?: AssistantAction;
  compact?: boolean;
  onSend: (message: string) => void;
}

const defaultPrompts = [
  "Research this asset",
  "Why did this move today?",
  "Compare this with AMD",
  "Open risk center"
];

export function AIChat({ context, messages, activities, action, compact = false, onSend }: AIChatProps) {
  const visibleMessages = compact ? messages.slice(-4) : messages;
  const visibleActivities = compact ? activities.slice(0, 3) : activities;

  return (
    <div className="flex h-full flex-col gap-3">
      <ContextBadge context={context} />
      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto rounded-md border border-atlas-line bg-atlas-void p-3">
        {visibleMessages.map((message) => (
          <AIMessage key={message.id} message={message} />
        ))}
      </div>

      {visibleActivities.length > 0 ? (
        <div className="space-y-2">
          {visibleActivities.map((activity) => (
            <ToolActivityCard key={activity.id} activity={activity} />
          ))}
        </div>
      ) : null}

      {action ? <ActionConfirmationCard action={action} /> : null}

      <SuggestedPrompts prompts={defaultPrompts} onSelect={onSend} />
      <AIInput compact={compact} onSend={onSend} />
    </div>
  );
}
