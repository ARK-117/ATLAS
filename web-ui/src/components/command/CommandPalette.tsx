import { useEffect, useMemo, useState } from "react";
import {
  Bot,
  BrainCircuit,
  ChartCandlestick,
  FileSearch,
  Flame,
  Keyboard,
  LayoutDashboard,
  LineChart,
  LockKeyhole,
  Microscope,
  Search,
  ShieldAlert
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ViewId } from "../../types";

interface CommandPaletteProps {
  activeView: ViewId;
  open: boolean;
  selectedSymbol: string;
  onAssistantSend: (message: string) => void;
  onOpenChange: (open: boolean) => void;
  onSelectAsset: (symbol: string) => void;
  onViewChange: (view: ViewId) => void;
}

interface CommandItem {
  id: string;
  label: string;
  detail: string;
  icon: LucideIcon;
  keywords: string;
  action: () => void;
}

const symbolPattern = /\b[A-Z]{1,5}\b/;

function normalize(value: string) {
  return value.trim().toLowerCase();
}

export function CommandPalette({
  activeView,
  open,
  selectedSymbol,
  onAssistantSend,
  onOpenChange,
  onSelectAsset,
  onViewChange
}: CommandPaletteProps) {
  const [query, setQuery] = useState("");

  const close = () => {
    setQuery("");
    onOpenChange(false);
  };

  const commands = useMemo<CommandItem[]>(
    () => [
      {
        id: "open-command-center",
        label: "Open Command Center",
        detail: "Return to the main mission-control dashboard.",
        icon: LayoutDashboard,
        keywords: "dashboard home overview command center",
        action: () => onViewChange("command-center")
      },
      {
        id: "open-ai-chat",
        label: "Open AI Chat",
        detail: "Use the full-screen ATLAS conversation surface.",
        icon: Bot,
        keywords: "assistant chat ai atlas ask",
        action: () => onViewChange("ai-chat")
      },
      {
        id: "open-research",
        label: "Open Research Lab",
        detail: "Research assets, compare symbols, and review agent debate.",
        icon: Microscope,
        keywords: "research compare report analysis",
        action: () => onViewChange("research-lab")
      },
      {
        id: "open-web-research",
        label: "Open Web Research",
        detail: "Source-grounded web research workspace. Backend tools are gated.",
        icon: FileSearch,
        keywords: "web sources citations news filings",
        action: () => onViewChange("web-research")
      },
      {
        id: "open-market-map",
        label: "Open Market Map",
        detail: "Visual map of watchlist, momentum, volatility, and AI attention.",
        icon: ChartCandlestick,
        keywords: "market heatmap map tiles movers",
        action: () => onViewChange("market-map")
      },
      {
        id: "open-asset",
        label: `Open ${selectedSymbol} Deep Dive`,
        detail: "Inspect chart workspace, research lenses, and asset timeline.",
        icon: LineChart,
        keywords: `asset chart deep dive ${selectedSymbol}`,
        action: () => onSelectAsset(selectedSymbol)
      },
      {
        id: "open-risk",
        label: "Open Risk Center",
        detail: "Review limits, warnings, restrictions, and emergency controls.",
        icon: ShieldAlert,
        keywords: "risk limits drawdown exposure kill switch",
        action: () => onViewChange("risk-center")
      },
      {
        id: "open-live",
        label: "Open Locked Live Trading",
        detail: "View the production-gated real-money workflow.",
        icon: LockKeyhole,
        keywords: "live trading broker order intent real money locked",
        action: () => onViewChange("live-trading")
      },
      {
        id: "ask-risk",
        label: `Ask ATLAS for ${selectedSymbol} risk`,
        detail: "Creates an assistant turn with tool activity and safety checks.",
        icon: BrainCircuit,
        keywords: `ask atlas risk explain ${selectedSymbol}`,
        action: () => onAssistantSend(`Review ${selectedSymbol} risk and portfolio impact`)
      },
      {
        id: "prepare-paper",
        label: `Prepare ${selectedSymbol} paper-trade idea`,
        detail: "Generates a safe paper order intent, not a live order.",
        icon: Flame,
        keywords: `paper trade idea order intent simulation ${selectedSymbol}`,
        action: () => onAssistantSend(`Prepare a paper trade idea for ${selectedSymbol}`)
      }
    ],
    [onAssistantSend, onSelectAsset, onViewChange, selectedSymbol]
  );

  const filteredCommands = useMemo(() => {
    const text = normalize(query);
    if (!text) {
      return commands;
    }
    return commands.filter((command) => normalize(`${command.label} ${command.detail} ${command.keywords}`).includes(text));
  }, [commands, query]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        onOpenChange(true);
      }
      if (event.key === "Escape") {
        onOpenChange(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onOpenChange]);

  useEffect(() => {
    if (!open) {
      setQuery("");
    }
  }, [open]);

  const runCommand = (command: CommandItem) => {
    command.action();
    close();
  };

  const runFreeform = () => {
    const cleanQuery = query.trim();
    if (!cleanQuery) {
      return;
    }
    const symbol = cleanQuery.match(symbolPattern)?.[0];
    if (symbol && /open|chart|deep dive|asset/i.test(cleanQuery)) {
      onSelectAsset(symbol);
    } else {
      onAssistantSend(cleanQuery);
    }
    close();
  };

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
      <div className="mx-auto mt-[8vh] max-w-2xl overflow-hidden rounded-lg border border-atlas-line bg-atlas-deck shadow-[0_24px_80px_rgba(0,0,0,0.46)]">
        <div className="flex items-center gap-3 border-b border-atlas-line px-4 py-3">
          <Search className="h-5 w-5 text-atlas-blue" aria-hidden="true" />
          <input
            autoFocus
            className="h-11 flex-1 bg-transparent text-base text-atlas-text outline-none placeholder:text-atlas-muted"
            placeholder="Type a command or ask ATLAS..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                const cleanQuery = query.trim();
                if (!cleanQuery && filteredCommands[0]) {
                  runCommand(filteredCommands[0]);
                } else if (/^(open|show|go to)\b/i.test(cleanQuery) && filteredCommands[0]) {
                  runCommand(filteredCommands[0]);
                } else {
                  runFreeform();
                }
              }
            }}
          />
          <div className="hidden items-center gap-2 rounded-md border border-atlas-line bg-white/[0.03] px-2 py-1 text-xs text-atlas-muted sm:flex">
            <Keyboard className="h-3.5 w-3.5" aria-hidden="true" />
            Ctrl K
          </div>
        </div>

        <div className="max-h-[420px] overflow-y-auto p-2">
          {filteredCommands.length === 0 ? (
            <button type="button" className="w-full rounded-md border border-atlas-line bg-white/[0.03] p-4 text-left" onClick={runFreeform}>
              <p className="text-sm font-semibold text-atlas-text">Ask ATLAS</p>
              <p className="mt-1 text-sm text-atlas-muted">{query || "Send a natural-language request to the assistant."}</p>
            </button>
          ) : (
            filteredCommands.map((command, index) => {
              const Icon = command.icon;
              const selected = index === 0;
              return (
                <button
                  key={command.id}
                  type="button"
                  className={`flex w-full items-start gap-3 rounded-md border p-3 text-left transition ${
                    selected
                      ? "border-atlas-blue/50 bg-atlas-blue/10"
                      : "border-transparent hover:border-atlas-line hover:bg-white/[0.04]"
                  }`}
                  onClick={() => runCommand(command)}
                >
                  <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-atlas-line bg-white/[0.03]">
                    <Icon className="h-4 w-4 text-atlas-blue" aria-hidden="true" />
                  </span>
                  <span className="min-w-0">
                    <span className="block text-sm font-semibold text-atlas-text">{command.label}</span>
                    <span className="mt-1 block text-sm text-atlas-muted">{command.detail}</span>
                  </span>
                </button>
              );
            })
          )}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-atlas-line px-4 py-3 text-xs text-atlas-muted">
          <span>Current view: {activeView.replace(/-/g, " ")}</span>
          <span>Freeform prompts are routed through the safe local assistant runtime.</span>
        </div>
      </div>
    </div>
  );
}
