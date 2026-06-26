export type ViewId =
  | "command-center"
  | "ai-chat"
  | "market-map"
  | "web-research"
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
export type AssistantRole = "user" | "assistant" | "system";
export type ToolStatus = "pending" | "success" | "failed" | "blocked";

export type AssistantIntent =
  | "general_chat"
  | "ui_help"
  | "research_asset"
  | "compare_assets"
  | "explain_asset_move"
  | "summarize_webpage"
  | "web_research"
  | "watchlist_action"
  | "portfolio_review"
  | "risk_review"
  | "create_research_report"
  | "create_paper_order_intent"
  | "create_live_order_intent"
  | "open_app_view"
  | "settings_action";

export interface AppContext {
  activeView: ViewId;
  selectedSymbol: string;
  selectedEntities: string[];
  mode: "Research" | "Paper" | "Live" | "Emergency";
  watchlistSummary: string[];
  portfolioSummary: {
    cash: string | null;
    positions: string[];
    riskState: RiskState;
  };
  recentQueries: string[];
  availableTools: string[];
}

export interface AssistantMessage {
  id: string;
  role: AssistantRole;
  content: string;
  timestamp: string;
}

export interface ToolActivity {
  id: string;
  toolName: string;
  status: ToolStatus;
  summary: string;
  timestamp: string;
  details?: string;
}

export interface AssistantAction {
  id: string;
  title: string;
  description: string;
  risk: RiskState;
  confirmLabel: string;
  cancelLabel: string;
}

export interface AssistantRuntimeResult {
  intent: AssistantIntent;
  entities: string[];
  message: AssistantMessage;
  activities: ToolActivity[];
  action?: AssistantAction;
  openView?: ViewId;
  selectedSymbol?: string;
}
