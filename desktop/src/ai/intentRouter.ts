import type { AppContext, AssistantIntent, ViewId } from "../types";

const symbolAliases: Record<string, string> = {
  nvidia: "NVDA",
  nvda: "NVDA",
  amd: "AMD",
  apple: "AAPL",
  aapl: "AAPL",
  microsoft: "MSFT",
  msft: "MSFT",
  tesla: "TSLA",
  tsla: "TSLA",
  spy: "SPY"
};

const viewAliases: Array<[ViewId, RegExp]> = [
  ["command-center", /\b(command|home|dashboard|center)\b/],
  ["ai-chat", /\b(ai chat|chat|conversation|assistant)\b/],
  ["research-lab", /\b(research lab|research)\b/],
  ["web-research", /\b(web research|web|internet|source|sources|news)\b/],
  ["watchlist", /\b(watchlist|watch list)\b/],
  ["asset-deep-dive", /\b(asset|deep dive|chart|stock page)\b/],
  ["portfolio", /\b(portfolio|positions|allocation)\b/],
  ["risk-center", /\b(risk|risk center|limits)\b/],
  ["paper-trading", /\b(paper|simulation|simulate)\b/],
  ["live-trading", /\b(live trading|live order|real money)\b/],
  ["backtesting", /\b(backtest|strategy test)\b/],
  ["agents", /\b(agent|agents|tools)\b/],
  ["audit", /\b(audit|logs|events)\b/],
  ["settings", /\b(settings|preferences|configuration)\b/]
];

export interface RoutedIntent {
  intent: AssistantIntent;
  entities: string[];
  targetView?: ViewId;
}

export function routeIntent(message: string, context: AppContext): RoutedIntent {
  const text = message.trim().toLowerCase();
  const entities = extractSymbols(text, context);

  const targetView = viewAliases.find(([, pattern]) => pattern.test(text))?.[0];
  if (/\b(open|show|go to|take me to|switch to)\b/.test(text) && targetView) {
    return { intent: "open_app_view", entities, targetView };
  }

  if (/\b(compare|versus|vs\.?|against)\b/.test(text)) {
    return { intent: "compare_assets", entities: ensureComparisonEntities(entities, context) };
  }

  if (/\b(why|moved|move today|moving|happened|what happened)\b/.test(text)) {
    return { intent: "explain_asset_move", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(web|internet|source|sources|news|today|latest|recent|article|website)\b/.test(text)) {
    if (/\b(summarize|summary|read this|this article|this website)\b/.test(text)) {
      return { intent: "summarize_webpage", entities };
    }
    return { intent: "web_research", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(research|look into|thesis|strong|weak|bull|bear|report)\b/.test(text)) {
    if (/\b(report|write this up|save it|make a report)\b/.test(text)) {
      return { intent: "create_research_report", entities: ensureSelectedEntity(entities, context) };
    }
    return { intent: "research_asset", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(add|remove|watchlist|watch list)\b/.test(text)) {
    return { intent: "watchlist_action", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(portfolio|positions|allocation|exposure)\b/.test(text)) {
    return { intent: "portfolio_review", entities };
  }

  if (/\b(risk|downside|danger|stop loss|stop-loss|before entering)\b/.test(text)) {
    return { intent: "risk_review", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(paper trade|paper order|simulate trade|trade idea)\b/.test(text)) {
    return { intent: "create_paper_order_intent", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(live trade|live order|place this|buy this|sell this)\b/.test(text)) {
    return { intent: "create_live_order_intent", entities: ensureSelectedEntity(entities, context) };
  }

  if (/\b(help|how do i|what can you do)\b/.test(text)) {
    return { intent: "ui_help", entities };
  }

  return { intent: "general_chat", entities: ensureSelectedEntity(entities, context) };
}

function extractSymbols(text: string, context: AppContext): string[] {
  const found = new Set<string>();
  Object.entries(symbolAliases).forEach(([alias, symbol]) => {
    if (new RegExp(`\\b${alias}\\b`, "i").test(text)) {
      found.add(symbol);
    }
  });

  const explicitTickers = text.match(/\b[A-Z]{1,5}\b/g) ?? [];
  explicitTickers.forEach((ticker) => found.add(ticker));

  if (/\b(this|it|that stock|selected asset)\b/.test(text) && context.selectedSymbol) {
    found.add(context.selectedSymbol);
  }

  return Array.from(found);
}

function ensureSelectedEntity(entities: string[], context: AppContext): string[] {
  return entities.length > 0 ? entities : [context.selectedSymbol];
}

function ensureComparisonEntities(entities: string[], context: AppContext): string[] {
  if (entities.length >= 2) {
    return entities;
  }
  if (entities.length === 1 && entities[0] !== context.selectedSymbol) {
    return [context.selectedSymbol, entities[0]];
  }
  return [context.selectedSymbol, "AMD"];
}
