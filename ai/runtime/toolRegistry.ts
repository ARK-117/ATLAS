import type { AppContext, AssistantAction, RiskState, ToolActivity, ViewId } from "./types";

const toolDescriptions: Record<string, string> = {
  web_search: "Search current public web sources through the backend web tool.",
  fetch_webpage: "Fetch and extract a web page through a controlled backend tool.",
  summarize_webpage: "Summarize a fetched page with source metadata.",
  get_quote: "Fetch a quote from the configured market-data provider.",
  get_news: "Fetch recent news from configured sources.",
  add_to_watchlist: "Add a symbol to the local watchlist.",
  open_view: "Navigate the desktop workspace to a safe view.",
  create_research_report: "Create a source-aware research report.",
  risk_check: "Run deterministic risk checks before any order intent.",
  create_paper_order_intent: "Prepare a paper-trading order intent.",
  create_live_order_intent: "Prepare a live order intent without submitting it."
};

export function listToolDescriptions() {
  return toolDescriptions;
}

export function createToolActivity(toolName: string, status: ToolActivity["status"], summary: string, details?: string): ToolActivity {
  return {
    id: makeId("tool"),
    toolName,
    status,
    summary,
    details,
    timestamp: new Date().toLocaleTimeString()
  };
}

export function createConfirmationAction(title: string, description: string, risk: RiskState): AssistantAction {
  return {
    id: makeId("action"),
    title,
    description,
    risk,
    confirmLabel: risk === "blocked" ? "Review requirements" : "Confirm",
    cancelLabel: "Cancel"
  };
}

export function toolUnavailableActivity(toolName: string): ToolActivity {
  return createToolActivity(
    toolName,
    "blocked",
    "Backend tool is not connected yet.",
    "ATLAS will not invent tool output. Connect the FastAPI tool endpoint before using live web or market data."
  );
}

export function safeOpenViewActivity(targetView: ViewId): ToolActivity {
  return createToolActivity("open_view", "success", `Opened ${targetView.replace(/-/g, " ")}.`);
}

export function contextSummary(context: AppContext) {
  return `View: ${context.activeView}. Selected asset: ${context.selectedSymbol}. Mode: ${context.mode}. Watchlist: ${context.watchlistSummary.join(", ")}.`;
}

export function makeId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}
