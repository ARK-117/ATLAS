import type { ReactNode } from "react";
import type { AppContext, AssistantAction, AssistantMessage, ToolActivity, ViewId } from "../types";
import { BottomConsole } from "./BottomConsole";
import { RightAIPanel } from "./RightAIPanel";
import { Sidebar } from "./Sidebar";
import { TopStatusBar } from "./TopStatusBar";

interface AppShellProps {
  activeView: ViewId;
  assistantAction?: AssistantAction;
  assistantActivities: ToolActivity[];
  assistantContext: AppContext;
  assistantMessages: AssistantMessage[];
  onViewChange: (view: ViewId) => void;
  onAssistantSend: (message: string) => void;
  children: ReactNode;
}

export function AppShell({
  activeView,
  assistantAction,
  assistantActivities,
  assistantContext,
  assistantMessages,
  onViewChange,
  onAssistantSend,
  children
}: AppShellProps) {
  return (
    <div className="grid h-screen grid-cols-[188px_minmax(0,1fr)] grid-rows-[64px_minmax(0,1fr)_132px] overflow-hidden bg-atlas-void text-atlas-text xl:grid-cols-[188px_minmax(0,1fr)_380px]">
      <Sidebar activeView={activeView} onViewChange={onViewChange} />
      <TopStatusBar context={assistantContext} />
      <main className="col-start-2 col-end-3 row-start-2 row-end-3 overflow-y-auto p-5">{children}</main>
      <RightAIPanel
        context={assistantContext}
        messages={assistantMessages}
        activities={assistantActivities}
        action={assistantAction}
        onSend={onAssistantSend}
      />
      <BottomConsole activities={assistantActivities} />
    </div>
  );
}
