import type { AppContext, ViewId } from "./types";

const availableTools = [
  "web_search",
  "fetch_webpage",
  "summarize_webpage",
  "get_quote",
  "get_news",
  "add_to_watchlist",
  "remove_from_watchlist",
  "open_view",
  "create_research_report",
  "risk_check",
  "create_paper_order_intent",
  "create_live_order_intent"
];

interface BuildAppContextInput {
  activeView: ViewId;
  selectedSymbol: string;
  recentQueries: string[];
  watchlist: string[];
}

export function buildAppContext({
  activeView,
  selectedSymbol,
  recentQueries,
  watchlist
}: BuildAppContextInput): AppContext {
  return {
    activeView,
    selectedSymbol,
    selectedEntities: selectedSymbol ? [selectedSymbol] : [],
    mode: "Research",
    watchlistSummary: watchlist,
    portfolioSummary: {
      cash: "$100,000 preview",
      positions: [],
      riskState: "normal"
    },
    recentQueries: recentQueries.slice(-6),
    availableTools
  };
}
