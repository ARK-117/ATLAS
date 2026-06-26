import {
  Activity,
  Bot,
  Briefcase,
  Command,
  FileText,
  FlaskConical,
  Grid3X3,
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
  { id: "market-map", label: "Market Map", icon: Grid3X3 },
  { id: "watchlist", label: "Watchlist", icon: ListChecks },
  { id: "asset-deep-dive", label: "Asset Deep Dive", icon: LineChart },
  { id: "research-lab", label: "Research Lab", icon: Microscope },
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
    <aside className="row-span-3 flex h-screen w-[76px] flex-col border-r border-atlas-line bg-atlas-deck">
      <div className="flex h-16 items-center justify-center border-b border-atlas-line">
        <div className="flex h-10 w-10 items-center justify-center rounded-md border border-atlas-cyan/40 bg-atlas-cyan/10">
          <Command className="h-5 w-5 text-atlas-cyan" aria-hidden="true" />
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-2 py-3">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = activeView === item.id;
          return (
            <button
              key={item.id}
              type="button"
              className={`group relative flex h-11 w-full items-center justify-center rounded-md border text-atlas-muted transition ${
                active
                  ? "border-atlas-cyan/60 bg-atlas-cyan/10 text-atlas-cyan shadow-glow"
                  : "border-transparent hover:border-atlas-line hover:bg-white/5 hover:text-atlas-text"
              }`}
              onClick={() => onViewChange(item.id)}
              aria-label={item.label}
              title={item.label}
            >
              <Icon className="h-5 w-5" aria-hidden="true" />
              <span className="pointer-events-none absolute left-[60px] z-20 hidden min-w-max rounded-md border border-atlas-line bg-atlas-panel px-2 py-1 text-xs text-atlas-text shadow-lg group-hover:block">
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-atlas-line p-2">
        <div className="flex h-10 items-center justify-center rounded-md border border-atlas-line bg-white/[0.03]">
          <Activity className="h-4 w-4 text-atlas-green" aria-hidden="true" />
        </div>
      </div>
    </aside>
  );
}
