import { useEffect, useState } from "react";
import { buildAppContext } from "../../ai/runtime/contextBuilder";
import { runAssistantTurn, userMessage } from "../../ai/runtime/assistantRuntime";
import { CommandPalette } from "./components/command/CommandPalette";
import { AppShell } from "./layout/AppShell";
import { AIChatPage } from "./pages/AIChatPage";
import { Agents } from "./pages/Agents";
import { AssetDeepDive } from "./pages/AssetDeepDive";
import { AuditLogs } from "./pages/AuditLogs";
import { BacktestingLab } from "./pages/BacktestingLab";
import { CommandCenter } from "./pages/CommandCenter";
import { LiveTrading } from "./pages/LiveTrading";
import { MarketMap } from "./pages/MarketMap";
import { PaperTrading } from "./pages/PaperTrading";
import { Portfolio } from "./pages/Portfolio";
import { ResearchLab } from "./pages/ResearchLab";
import { RiskCenter } from "./pages/RiskCenter";
import { Settings } from "./pages/Settings";
import { Watchlist } from "./pages/Watchlist";
import { WebResearch } from "./pages/WebResearch";
import { fetchAtlasStatus, sendAssistantTurn } from "./services/api";
import type { AtlasStatus } from "./services/api";
import type { AssistantAction, AssistantMessage, ToolActivity, ViewId } from "./types";

const initialAssistantMessages: AssistantMessage[] = [
  {
    id: "assistant-welcome",
    role: "assistant",
    content:
      "I'm ATLAS. You can speak normally: ask me to research an asset, compare symbols, explain risk, open a view, or prepare a safe paper-trade idea. I'll show tool activity and won't invent data.",
    timestamp: new Date().toLocaleTimeString()
  }
];

const initialBackendStatus: AtlasStatus = {
  mode: "Research Mode",
  broker: "Disconnected",
  market: "Monitoring",
  dataFreshness: "Checking backend",
  ai: "Checking backend",
  risk: "Normal",
  killSwitchActive: false,
  connected: false
};

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>("command-center");
  const [selectedSymbol, setSelectedSymbol] = useState("NVDA");
  const [assistantMessages, setAssistantMessages] = useState<AssistantMessage[]>(initialAssistantMessages);
  const [assistantActivities, setAssistantActivities] = useState<ToolActivity[]>([]);
  const [assistantAction, setAssistantAction] = useState<AssistantAction | undefined>();
  const [recentQueries, setRecentQueries] = useState<string[]>([]);
  const [commandOpen, setCommandOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<AtlasStatus>(initialBackendStatus);

  useEffect(() => {
    let active = true;

    const refreshStatus = async () => {
      const status = await fetchAtlasStatus();
      if (active) {
        setBackendStatus(status);
      }
    };

    void refreshStatus();
    const interval = window.setInterval(() => {
      void refreshStatus();
    }, 15_000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const assistantContext = buildAppContext({
    activeView,
    selectedSymbol,
    recentQueries,
    watchlist: ["NVDA", "AAPL", "MSFT", "TSLA", "AMD", "SPY"]
  });

  const openAsset = (symbol: string) => {
    setSelectedSymbol(symbol);
    setActiveView("asset-deep-dive");
  };

  const handleAssistantSend = async (content: string) => {
    const outgoing = userMessage(content);
    const context = buildAppContext({
      activeView,
      selectedSymbol,
      recentQueries: [...recentQueries, content],
      watchlist: ["NVDA", "AAPL", "MSFT", "TSLA", "AMD", "SPY"]
    });

    setAssistantMessages((messages) => [...messages, outgoing]);
    setRecentQueries((queries) => [...queries, content].slice(-8));

    let result;
    try {
      result = await sendAssistantTurn(content, context);
      const status = await fetchAtlasStatus();
      setBackendStatus(status);
    } catch {
      result = runAssistantTurn(content, context);
    }

    setAssistantMessages((messages) => [...messages, result.message]);
    setAssistantActivities((activities) => [...result.activities, ...activities].slice(0, 12));
    setAssistantAction(result.action);

    if (result.selectedSymbol) {
      setSelectedSymbol(result.selectedSymbol);
    }
    if (result.openView) {
      setActiveView(result.openView);
    }
  };

  const renderView = () => {
    switch (activeView) {
      case "ai-chat":
        return (
          <AIChatPage
            context={assistantContext}
            messages={assistantMessages}
            activities={assistantActivities}
            action={assistantAction}
            onSend={handleAssistantSend}
          />
        );
      case "market-map":
        return <MarketMap onSelectAsset={openAsset} />;
      case "web-research":
        return <WebResearch context={assistantContext} status={backendStatus} onSend={handleAssistantSend} />;
      case "watchlist":
        return <Watchlist onSelectAsset={openAsset} />;
      case "asset-deep-dive":
        return <AssetDeepDive symbol={selectedSymbol} />;
      case "research-lab":
        return <ResearchLab />;
      case "portfolio":
        return <Portfolio />;
      case "risk-center":
        return <RiskCenter />;
      case "paper-trading":
        return <PaperTrading />;
      case "live-trading":
        return <LiveTrading />;
      case "backtesting":
        return <BacktestingLab />;
      case "agents":
        return <Agents />;
      case "audit":
        return <AuditLogs />;
      case "settings":
        return <Settings />;
      case "command-center":
      default:
        return <CommandCenter onSelectAsset={openAsset} />;
    }
  };

  return (
    <AppShell
      activeView={activeView}
      assistantAction={assistantAction}
      assistantActivities={assistantActivities}
      assistantContext={assistantContext}
      assistantMessages={assistantMessages}
      backendStatus={backendStatus}
      onAssistantSend={handleAssistantSend}
      onCommandOpen={() => setCommandOpen(true)}
      onViewChange={setActiveView}
    >
      {renderView()}
      <CommandPalette
        activeView={activeView}
        open={commandOpen}
        selectedSymbol={selectedSymbol}
        onAssistantSend={handleAssistantSend}
        onOpenChange={setCommandOpen}
        onSelectAsset={openAsset}
        onViewChange={setActiveView}
      />
    </AppShell>
  );
}
