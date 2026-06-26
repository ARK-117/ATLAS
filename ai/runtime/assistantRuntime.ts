import type { AppContext, AssistantMessage, AssistantRuntimeResult } from "./types";
import { routeIntent } from "./intentRouter";
import {
  contextSummary,
  createConfirmationAction,
  createToolActivity,
  makeId,
  safeOpenViewActivity,
  toolUnavailableActivity
} from "./toolRegistry";

export function runAssistantTurn(userMessage: string, context: AppContext): AssistantRuntimeResult {
  const routed = routeIntent(userMessage, context);
  const primarySymbol = routed.entities[0] ?? context.selectedSymbol;
  const activities = [createToolActivity("context_builder", "success", contextSummary(context))];
  let content = "";

  switch (routed.intent) {
    case "open_app_view":
      if (routed.targetView) {
        activities.push(safeOpenViewActivity(routed.targetView));
        content = `I understood that you want to open ${routed.targetView.replace(/-/g, " ")}. I switched the workspace there.`;
        return {
          intent: routed.intent,
          entities: routed.entities,
          activities,
          message: assistantMessage(content),
          openView: routed.targetView
        };
      }
      content = "I can open an app view, but I need to know which view you want.";
      break;

    case "research_asset":
      activities.push(toolUnavailableActivity("get_quote"));
      activities.push(toolUnavailableActivity("get_news"));
      content =
        `I'll treat this as a research request for ${primarySymbol}. The local backend is offline, so I will not invent prices or news.\n\n` +
        "Summary: I can preserve the research intent and use the selected app context now.\n\n" +
        "What to check next: start the ATLAS backend, then I can use source-backed quote and web tools.";
      break;

    case "compare_assets":
      activities.push(toolUnavailableActivity("get_quote"));
      content =
        `I'll compare ${routed.entities.join(" vs ")} using strength, risk, valuation context, catalysts, and portfolio impact once backend data tools are reachable. ` +
        "For now, I am preserving the comparison request and not fabricating market facts.";
      break;

    case "explain_asset_move":
      activities.push(toolUnavailableActivity("get_news"));
      activities.push(toolUnavailableActivity("get_price_history"));
      content =
        `I'll treat "this" as ${primarySymbol}. To explain why it moved today, ATLAS needs recent price movement, news, market context, and event data. ` +
        "Those tools are unavailable while the backend is offline, so I am not making up a catalyst.";
      break;

    case "web_research":
      activities.push(toolUnavailableActivity("web_search"));
      content =
        `I understood this as current web research for ${primarySymbol}. Web research should run through controlled backend tools with source cards and citations. ` +
        "The backend is offline, so I am showing the planned tool call instead of pretending I searched.";
      break;

    case "summarize_webpage":
      activities.push(toolUnavailableActivity("fetch_webpage"));
      activities.push(toolUnavailableActivity("summarize_webpage"));
      content = "I can summarize a webpage once you provide a URL and the backend fetch tool is reachable. I will not summarize a page I cannot fetch.";
      break;

    case "watchlist_action":
      activities.push(createToolActivity("watchlist_action", "pending", `Prepared a watchlist action for ${primarySymbol}.`));
      content = `I understood this as a watchlist action for ${primarySymbol}. Adding is safe, but removing or changing notes should be confirmed.`;
      return {
        intent: routed.intent,
        entities: routed.entities,
        activities,
        message: assistantMessage(content),
        action: createConfirmationAction(
          `Update watchlist for ${primarySymbol}`,
          "ATLAS can update the local watchlist after backend persistence is connected.",
          "normal"
        )
      };

    case "risk_review":
      activities.push(toolUnavailableActivity("risk_check"));
      content =
        `I'll review risk for ${primarySymbol}. The right checks are position concentration, liquidity, volatility, event risk, stale data, and portfolio impact. ` +
        "The deterministic risk engine remains the authority before any order intent.";
      break;

    case "portfolio_review":
      activities.push(toolUnavailableActivity("get_portfolio_summary"));
      content = "I can review portfolio concentration, exposures, correlation, and drawdown once portfolio data is connected. I will not invent holdings.";
      break;

    case "create_research_report":
      activities.push(createToolActivity("create_research_report", "pending", `Prepared report outline for ${primarySymbol}.`));
      content =
        `I can create a report for ${primarySymbol}. It should include summary, key findings, bull case, bear case, risks, uncertainty, and next checks. ` +
        "Source-backed sections need backend web and market tools first.";
      break;

    case "create_paper_order_intent":
      activities.push(toolUnavailableActivity("risk_check"));
      content =
        `I can prepare a paper-trading idea for ${primarySymbol}, but it must show expected max loss, stop-loss, thesis, and risk result before submission.`;
      return {
        intent: routed.intent,
        entities: routed.entities,
        activities,
        message: assistantMessage(content),
        action: createConfirmationAction(
          `Prepare paper order intent for ${primarySymbol}`,
          "This would create a simulation-only intent after deterministic risk checks are connected.",
          "caution"
        )
      };

    case "create_live_order_intent":
      activities.push(createToolActivity("live_permission_gate", "blocked", "Live order submission is locked."));
      content =
        "I can prepare a live order intent only after production mode, broker credentials, risk checks, and human approval are configured. I will not submit a live order silently.";
      return {
        intent: routed.intent,
        entities: routed.entities,
        activities,
        message: assistantMessage(content),
        action: createConfirmationAction(
          "Live action requires approval",
          "Live trading is blocked until the full production safety gate is configured.",
          "blocked"
        )
      };

    case "ui_help":
      content =
        'You can speak naturally. Try: "research Nvidia", "why did this move today", "compare NVDA and AMD", "open risk center", or "what should I check before entering this trade?"';
      break;

    case "settings_action":
      content = "Settings changes should go through an explicit settings workflow. I can explain the current setting, but sensitive changes need confirmation.";
      break;

    case "general_chat":
    default:
      content =
        `I'm with you. Current context is ${context.activeView} with ${context.selectedSymbol} selected. ` +
        "Ask normally and I will infer the task, use app context, and show tool activity when tools are needed.";
      break;
  }

  return {
    intent: routed.intent,
    entities: routed.entities,
    activities,
    message: assistantMessage(content)
  };
}

export function userMessage(content: string): AssistantMessage {
  return {
    id: makeId("user"),
    role: "user",
    content,
    timestamp: new Date().toLocaleTimeString()
  };
}

function assistantMessage(content: string): AssistantMessage {
  return {
    id: makeId("assistant"),
    role: "assistant",
    content,
    timestamp: new Date().toLocaleTimeString()
  };
}
