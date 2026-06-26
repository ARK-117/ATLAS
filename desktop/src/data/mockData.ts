import type { AgentActivity, AuditEvent, MarketTileData, Metric } from "../types";

export const systemStatus = {
  mode: "Research Mode",
  broker: "Disconnected",
  market: "Monitoring",
  dataFreshness: "UI mock data",
  ai: "Backend pending",
  risk: "Normal",
  killSwitch: "Inactive",
  packaging: "MSVC linker required"
};

export const commandMetrics: Metric[] = [
  { label: "Portfolio Value", value: "$100,000.00", detail: "simulation baseline", trend: "flat" },
  { label: "Daily P/L", value: "$0.00", detail: "no live broker linked", trend: "flat" },
  { label: "Open Positions", value: "0", detail: "live execution locked", trend: "flat" },
  { label: "Risk Score", value: "18 / 100", detail: "normal controls", trend: "up" },
  { label: "Buying Power", value: "$0.00", detail: "broker not configured", trend: "flat" },
  { label: "AI Confidence", value: "Medium", detail: "source-grounded only", trend: "up" }
];

export const marketTiles: MarketTileData[] = [
  {
    symbol: "NVDA",
    name: "NVIDIA",
    price: "$127.40",
    change: "+1.84%",
    direction: "up",
    volume: "High",
    aiScore: 82,
    riskScore: 61,
    newsSignal: "Active"
  },
  {
    symbol: "MSFT",
    name: "Microsoft",
    price: "$471.22",
    change: "+0.42%",
    direction: "up",
    volume: "Normal",
    aiScore: 76,
    riskScore: 34,
    newsSignal: "Stable"
  },
  {
    symbol: "AAPL",
    name: "Apple",
    price: "$214.18",
    change: "-0.31%",
    direction: "down",
    volume: "Normal",
    aiScore: 64,
    riskScore: 41,
    newsSignal: "Muted"
  },
  {
    symbol: "TSLA",
    name: "Tesla",
    price: "$181.72",
    change: "-2.18%",
    direction: "down",
    volume: "Elevated",
    aiScore: 59,
    riskScore: 78,
    newsSignal: "Volatile"
  },
  {
    symbol: "AMD",
    name: "Advanced Micro Devices",
    price: "$158.06",
    change: "+0.96%",
    direction: "up",
    volume: "High",
    aiScore: 73,
    riskScore: 55,
    newsSignal: "Active"
  },
  {
    symbol: "SPY",
    name: "S&P 500 ETF",
    price: "$546.03",
    change: "+0.12%",
    direction: "flat",
    volume: "Normal",
    aiScore: 68,
    riskScore: 29,
    newsSignal: "Stable"
  }
];

export const watchlistRows = marketTiles.map((tile, index) => ({
  ...tile,
  marketCap: ["$3.1T", "$3.5T", "$3.2T", "$580B", "$255B", "$520B"][index],
  trend: ["Breakout", "Uptrend", "Range", "Weak", "Recovering", "Index base"][index],
  lastResearched: ["09:45", "09:28", "Yesterday", "08:57", "09:12", "09:01"][index]
}));

export const agents: AgentActivity[] = [
  {
    agent: "Router Agent",
    status: "Ready",
    task: "Classifying user workspace intent",
    confidence: 92
  },
  {
    agent: "Market Data Agent",
    status: "Waiting",
    task: "Backend quote service not connected",
    confidence: 64,
    warning: "Data freshness is a preview value"
  },
  {
    agent: "Risk Agent",
    status: "Active",
    task: "Enforcing locked live-trading boundary",
    confidence: 98
  },
  {
    agent: "Audit Agent",
    status: "Ready",
    task: "Canonical event stream available",
    confidence: 95
  }
];

export const auditEvents: AuditEvent[] = [
  {
    time: "10:06:11",
    type: "toolchain",
    subject: "Vite build passed",
    result: "desktop web bundle ready",
    risk: "normal"
  },
  {
    time: "10:04:19",
    type: "toolchain",
    subject: "Tauri packaging blocked",
    result: "MSVC linker missing",
    risk: "caution"
  },
  {
    time: "09:58:22",
    type: "governance",
    subject: "live trading locked",
    result: "blocked",
    risk: "blocked"
  },
  {
    time: "09:55:10",
    type: "risk",
    subject: "order-intent gate",
    result: "human approval required",
    risk: "caution"
  },
  {
    time: "09:50:43",
    type: "system",
    subject: "desktop shell",
    result: "preview started",
    risk: "normal"
  },
  {
    time: "09:48:07",
    type: "audit",
    subject: "canonical events",
    result: "append-only store ready",
    risk: "normal"
  }
];

export const researchReports = [
  {
    title: "NVDA AI Infrastructure Thesis",
    confidence: 74,
    risk: "caution" as const,
    summary:
      "Strong demand signals remain visible, but valuation, supply constraints, and event risk require controlled position sizing.",
    bull: "Data-center growth and software ecosystem expansion support continued leadership.",
    bear: "Multiple compression or weaker hyperscaler spending could invalidate the thesis."
  },
  {
    title: "TSLA Volatility Review",
    confidence: 58,
    risk: "high" as const,
    summary:
      "Momentum is unstable and headline sensitivity is elevated. ATLAS would require smaller risk and clearer invalidation.",
    bull: "Energy storage growth and operating leverage could improve sentiment.",
    bear: "Margin pressure, delivery uncertainty, and news shocks remain dominant risks."
  }
];

export const portfolioPositions = [
  { asset: "Cash", quantity: "-", avg: "-", price: "-", value: "$100,000.00", pnl: "$0.00", weight: "100%" },
  { asset: "NVDA", quantity: "0", avg: "-", price: "$127.40", value: "$0.00", pnl: "$0.00", weight: "0%" },
  { asset: "MSFT", quantity: "0", avg: "-", price: "$471.22", value: "$0.00", pnl: "$0.00", weight: "0%" }
];

export const riskControls = [
  { label: "Max daily loss", value: "1.0%", state: "normal" as const },
  { label: "Max drawdown", value: "8.0%", state: "normal" as const },
  { label: "Max single asset", value: "5.0%", state: "normal" as const },
  { label: "Sector concentration", value: "20.0%", state: "caution" as const },
  { label: "Live execution", value: "Locked", state: "blocked" as const },
  { label: "Broker credentials", value: "Not configured", state: "blocked" as const }
];

export const sparklinePoints = [16, 22, 18, 25, 24, 30, 27, 33, 31, 38, 35, 41];
