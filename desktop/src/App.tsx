import { useState } from "react";
import { AppShell } from "./layout/AppShell";
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
import type { ViewId } from "./types";

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>("command-center");
  const [selectedSymbol, setSelectedSymbol] = useState("NVDA");

  const openAsset = (symbol: string) => {
    setSelectedSymbol(symbol);
    setActiveView("asset-deep-dive");
  };

  const renderView = () => {
    switch (activeView) {
      case "market-map":
        return <MarketMap onSelectAsset={openAsset} />;
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
    <AppShell activeView={activeView} onViewChange={setActiveView}>
      {renderView()}
    </AppShell>
  );
}
