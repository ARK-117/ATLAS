import {
  Activity,
  Bot,
  Briefcase,
  Command,
  FileText,
  FlaskConical,
  Grid3X3,
  Globe2,
  LayoutDashboard,
  LineChart,
  ListChecks,
  LockKeyhole,
  Microscope,
  Settings,
  ShieldAlert,
  Wallet
} from "lucide-react";
import type { NavigationItem, ViewId } from "../types";

const navigation: NavigationItem[] = [
  { id: "command-center", label: "Command Center", icon: LayoutDashboard },
  { id: "ai-chat", label: "AI Chat", icon: Bot },
  { id: "research-lab", label: "Research Lab", icon: Microscope },
  { id: "web-research", label: "Web Research", icon: Globe2 },
  { id: "market-map", label: "Market Map", icon: Grid3X3 },
  { id: "watchlist", label: "Watchlist", icon: ListChecks },
  { id: "asset-deep-dive", label: "Asset Deep Dive", icon: LineChart },
  { id: "portfolio", label: "Portfolio", icon: Briefcase },
  { id: "risk-center", label: "Risk Center", icon: ShieldAlert },
  { id: "paper-trading", label: "Paper Trading", icon: Wallet },
  { id: "live-trading", label: "Live Trading", icon: LockKeyhole },
  { id: "backtesting", label: "Backtesting", icon: FlaskConical },
  { id: "agents", label: "AI Agents", icon: Bot },
  { id: "audit", label: "Audit Logs", icon: FileText },
  { id: "settings", label: "Settings", icon: Settings }
];

interface SidebarProps {
  activeView: ViewId;
  onViewChange: (view: ViewId) => void;
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  return (
    <aside className="row-span-3 flex h-screen w-[188px] flex-col border-r border-atlas-line bg-atlas-deck">
      <div className="flex h-16 items-center gap-3 border-b border-atlas-line px-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md border border-atlas-line bg-white/[0.03]">
          <Command className="h-4 w-4 text-atlas-blue" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <div className="text-sm font-semibold text-atlas-text">ATLAS</div>
          <div className="truncate text-xs text-atlas-muted">Local workstation</div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-2 py-3" aria-label="Main workspace">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = activeView === item.id;
          return (
            <button
              key={item.id}
              type="button"
              className={`flex h-9 w-full items-center gap-2 rounded-md border px-2 text-left text-sm text-atlas-muted transition ${
                active
                  ? "border-atlas-blue/50 bg-atlas-blue/10 text-atlas-text"
                  : "border-transparent hover:border-atlas-line hover:bg-white/5 hover:text-atlas-text"
              }`}
              onClick={() => onViewChange(item.id)}
            >
              <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-atlas-line p-2">
        <div className="flex h-10 items-center justify-center rounded-md border border-atlas-line bg-white/[0.03]">
          <Activity className="h-4 w-4 text-atlas-green" aria-hidden="true" />
          <span className="ml-2 text-xs text-atlas-muted">Research mode</span>
        </div>
      </div>
    </aside>
  );
}
