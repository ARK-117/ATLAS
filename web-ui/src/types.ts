import type { LucideIcon } from "lucide-react";
import type { RiskState, ViewId } from "../../ai/runtime/types";

export type {
  AppContext,
  AssistantAction,
  AssistantIntent,
  AssistantMessage,
  AssistantRole,
  AssistantRuntimeResult,
  RiskState,
  ToolActivity,
  ToolStatus,
  ViewId
} from "../../ai/runtime/types";

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
