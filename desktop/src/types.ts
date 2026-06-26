import type { LucideIcon } from "lucide-react";

export type ViewId =
  | "command-center"
  | "market-map"
  | "watchlist"
  | "asset-deep-dive"
  | "research-lab"
  | "portfolio"
  | "risk-center"
  | "paper-trading"
  | "live-trading"
  | "backtesting"
  | "agents"
  | "audit"
  | "settings";

export type RiskState = "normal" | "caution" | "high" | "blocked" | "emergency";
export type Direction = "up" | "down" | "flat";

export interface NavigationItem {
  id: ViewId;
  label: string;
  icon: LucideIcon;
}

export interface Metric {
  label: string;
  value: string;
  detail: string;
  trend: Direction;
}

export interface MarketTileData {
  symbol: string;
  name: string;
  price: string;
  change: string;
  direction: Direction;
  volume: string;
  aiScore: number;
  riskScore: number;
  newsSignal: string;
}

export interface AgentActivity {
  agent: string;
  status: string;
  task: string;
  confidence: number;
  warning?: string;
}

export interface AuditEvent {
  time: string;
  type: string;
  subject: string;
  result: string;
  risk: RiskState;
}
