import type { ReactNode } from "react";
import type { ViewId } from "../types";
import { BottomConsole } from "./BottomConsole";
import { RightAIPanel } from "./RightAIPanel";
import { Sidebar } from "./Sidebar";
import { TopStatusBar } from "./TopStatusBar";

interface AppShellProps {
  activeView: ViewId;
  onViewChange: (view: ViewId) => void;
  children: ReactNode;
}

export function AppShell({ activeView, onViewChange, children }: AppShellProps) {
  return (
    <div className="grid h-screen grid-cols-[76px_minmax(0,1fr)] grid-rows-[64px_minmax(0,1fr)_132px] overflow-hidden bg-atlas-void text-atlas-text xl:grid-cols-[76px_minmax(0,1fr)_360px]">
      <Sidebar activeView={activeView} onViewChange={onViewChange} />
      <TopStatusBar />
      <main className="col-start-2 col-end-3 row-start-2 row-end-3 overflow-y-auto p-5">{children}</main>
      <RightAIPanel />
      <BottomConsole />
    </div>
  );
}
