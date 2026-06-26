from __future__ import annotations

import json
import re
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app as atlas_app


HOST = "127.0.0.1"
PORT = 8000
DEFAULT_WATCHLIST = ["NVDA", "AAPL", "MSFT", "TSLA", "AMD", "SPY"]
SYMBOL_PATTERN = re.compile(r"\b[A-Z]{1,5}\b")

VIEW_TARGETS = {
    "command center": "command-center",
    "dashboard": "command-center",
    "ai chat": "ai-chat",
    "assistant": "ai-chat",
    "market map": "market-map",
    "web research": "web-research",
    "watchlist": "watchlist",
    "asset": "asset-deep-dive",
    "deep dive": "asset-deep-dive",
    "research": "research-lab",
    "portfolio": "portfolio",
    "risk": "risk-center",
    "risk center": "risk-center",
    "paper": "paper-trading",
    "paper trading": "paper-trading",
    "live": "live-trading",
    "live trading": "live-trading",
    "backtest": "backtesting",
    "backtesting": "backtesting",
    "agents": "agents",
    "audit": "audit",
    "settings": "settings",
}


def now_label() -> str:
    return atlas_app.datetime.now().strftime("%I:%M:%S %p").lstrip("0")


def make_id(prefix: str) -> str:
    return f"{prefix}-{int(atlas_app.datetime.now().timestamp() * 1000)}"


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw or "{}")


def activity(tool_name: str, status: str, summary: str, details: str = "") -> dict[str, Any]:
    return {
        "id": make_id("tool"),
        "toolName": tool_name,
        "status": status,
        "summary": summary,
        "details": details or None,
        "timestamp": now_label(),
    }


def assistant_message(content: str) -> dict[str, Any]:
    return {
        "id": make_id("assistant"),
        "role": "assistant",
        "content": content,
        "timestamp": now_label(),
    }


def confirmation_action(title: str, description: str, risk: str) -> dict[str, Any]:
    return {
        "id": make_id("action"),
        "title": title,
        "description": description,
        "risk": risk,
        "confirmLabel": "Review requirements" if risk == "blocked" else "Confirm",
        "cancelLabel": "Cancel",
    }


def load_status() -> dict[str, Any]:
    data = atlas_app.load_data()
    kill_switch_active = bool(data.get("system_controls", {}).get("kill_switch_active"))
    risk = "Emergency" if kill_switch_active else "Normal"
    web_ready = atlas_app.DDGS is not None
    quote_ready = atlas_app.yf is not None

    return {
        "mode": "Research Mode",
        "broker": "Disconnected",
        "market": "Monitoring",
        "dataFreshness": "Backend connected",
        "ai": "Backend online",
        "risk": risk,
        "killSwitchActive": kill_switch_active,
        "tools": {
            "quote": quote_ready,
            "webSearch": web_ready,
            "webpageFetch": atlas_app.trafilatura is not None,
            "liveTrading": False,
        },
    }


def watchlist_payload() -> dict[str, Any]:
    data = atlas_app.load_data()
    symbols = data.get("watchlist") or DEFAULT_WATCHLIST
    return {"symbols": symbols, "source": "atlas_data.json" if data.get("watchlist") else "default-preview"}


def quote_payload(symbol: str) -> dict[str, Any]:
    symbol = clean_symbol(symbol)
    if atlas_app.yf is None:
        return {
            "symbol": symbol,
            "available": False,
            "error": "yfinance is not installed in the active Python environment.",
        }

    snapshot = atlas_app.get_market_snapshot(symbol)
    if snapshot is None:
        return {
            "symbol": symbol,
            "available": False,
            "error": "No quote was returned by the configured market-data provider.",
        }

    return {
        "symbol": snapshot.symbol,
        "available": True,
        "price": snapshot.price,
        "timestamp": snapshot.timestamp.isoformat(),
        "source": snapshot.source,
        "averageDailyDollarVolume": snapshot.average_daily_dollar_volume,
        "assetClass": snapshot.asset_class.value,
    }


def web_search_payload(query: str, max_results: int = 5) -> dict[str, Any]:
    if atlas_app.DDGS is None:
        return {
            "query": query,
            "available": False,
            "error": "ddgs is not installed in the active Python environment.",
            "results": [],
        }

    results = atlas_app.web_search(query, max_results=max(1, min(max_results, 8)))
    return {"query": query, "available": True, "results": results}


def webpage_payload(url: str) -> dict[str, Any]:
    text = atlas_app.read_webpage(url)
    return {
        "url": url,
        "available": bool(text),
        "text": text[:12000],
        "error": "" if text else "No extractable page text returned.",
    }


def clean_symbol(value: str) -> str:
    return value.upper().replace("$", "").strip()[:8]


def extract_symbols(message: str, selected_symbol: str) -> list[str]:
    found = [clean_symbol(item) for item in SYMBOL_PATTERN.findall(message.upper())]
    ignored = {"AI", "UI", "API", "CEO", "USA", "THE", "WHY", "THIS"}
    symbols = [item for item in found if item not in ignored]
    if not symbols and selected_symbol:
        symbols = [clean_symbol(selected_symbol)]
    return list(dict.fromkeys(symbols))


def classify_intent(message: str) -> str:
    text = message.lower()
    if any(token in text for token in ["open ", "show "]):
        return "open_app_view"
    if "compare" in text or " vs " in text:
        return "compare_assets"
    if "why" in text and "move" in text:
        return "explain_asset_move"
    if "web research" in text or "search web" in text or "latest news" in text:
        return "web_research"
    if "live" in text and ("trade" in text or "order" in text):
        return "create_live_order_intent"
    if "paper" in text and ("trade" in text or "order" in text or "idea" in text):
        return "create_paper_order_intent"
    if "risk" in text:
        return "risk_review"
    if "portfolio" in text:
        return "portfolio_review"
    if "research" in text or "stock" in text or "asset" in text:
        return "research_asset"
    return "general_chat"


def target_view_for(message: str) -> str | None:
    text = message.lower()
    for label, view_id in VIEW_TARGETS.items():
        if label in text:
            return view_id
    return None


def quote_activity(symbol: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        quote = quote_payload(symbol)
    except Exception as error:  # pragma: no cover - defensive server boundary
        return activity("get_quote", "failed", f"Quote lookup failed for {symbol}.", str(error)), None

    if quote.get("available"):
        price = quote.get("price")
        source = quote.get("source", "market-data provider")
        return activity("get_quote", "success", f"{symbol} quote loaded: ${price:,.2f}.", f"Source: {source}"), quote

    return activity("get_quote", "failed", f"Quote unavailable for {symbol}.", quote.get("error", "")), quote


def search_activity(query: str, limit: int = 3) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        payload = web_search_payload(query, limit)
    except Exception as error:  # pragma: no cover - network/provider boundary
        return activity("web_search", "failed", "Web search failed.", str(error)), []

    if not payload.get("available"):
        return activity("web_search", "failed", "Web search unavailable.", payload.get("error", "")), []

    results = payload.get("results", [])
    return activity("web_search", "success", f"Found {len(results)} public web result(s).", query), results


def format_sources(results: list[dict[str, Any]]) -> str:
    if not results:
        return "Sources: none returned by the web tool."
    lines = ["Sources:"]
    for index, result in enumerate(results, start=1):
        title = result.get("title") or "Untitled"
        url = result.get("url") or ""
        snippet = result.get("snippet") or ""
        lines.append(f"{index}. {title}\n   {url}\n   {snippet[:240]}")
    return "\n".join(lines)


def assistant_turn(payload: dict[str, Any]) -> dict[str, Any]:
    message = str(payload.get("message", "")).strip()
    context = payload.get("context") or {}
    selected_symbol = clean_symbol(str(context.get("selectedSymbol", "NVDA")))
    symbols = extract_symbols(message, selected_symbol)
    primary = symbols[0] if symbols else selected_symbol
    intent = classify_intent(message)

    activities = [
        activity(
            "context_builder",
            "success",
            f"Backend received context. View: {context.get('activeView', 'unknown')}. Selected asset: {selected_symbol}.",
        )
    ]

    if intent == "open_app_view":
        view_id = target_view_for(message)
        if view_id:
            activities.append(activity("open_view", "success", f"Opened {view_id.replace('-', ' ')}."))
            return {
                "intent": intent,
                "entities": symbols,
                "activities": activities,
                "message": assistant_message(f"I opened {view_id.replace('-', ' ')}."),
                "openView": view_id,
            }

    if intent == "compare_assets":
        compared = symbols[:4] or [primary]
        quote_lines = []
        for symbol in compared:
            quote_log, quote = quote_activity(symbol)
            activities.append(quote_log)
            if quote and quote.get("available"):
                quote_lines.append(f"- {symbol}: ${quote['price']:,.2f} from {quote['source']}")
            else:
                quote_lines.append(f"- {symbol}: quote unavailable")
        content = "ATLAS backend comparison check:\n" + "\n".join(quote_lines)
        content += "\n\nThis is research support only. Portfolio impact and risk limits still need deterministic checks."
        return {
            "intent": intent,
            "entities": compared,
            "activities": activities,
            "message": assistant_message(content),
        }

    if intent in {"research_asset", "explain_asset_move", "web_research"}:
        quote_log, quote = quote_activity(primary)
        activities.append(quote_log)

        query = (
            f"{primary} stock latest news earnings financial performance risks"
            if intent != "explain_asset_move"
            else f"why did {primary} stock move today latest news market reaction"
        )
        if intent == "web_research" and message:
            query = message.replace("web research:", "").strip() or query

        search_log, results = search_activity(query, 4)
        activities.append(search_log)

        quote_text = "Quote: unavailable."
        if quote and quote.get("available"):
            quote_text = f"Quote: {primary} last delayed close ${quote['price']:,.2f} from {quote['source']} at {quote['timestamp']}."

        content = (
            f"ATLAS backend is connected for {primary}.\n\n"
            f"{quote_text}\n\n"
            "Research readout:\n"
            "- I used the local backend tool layer instead of UI-only mock data.\n"
            "- Treat web results as research leads until reviewed against filings, earnings, and licensed market data.\n"
            "- No live trading action was created.\n\n"
            f"{format_sources(results)}"
        )
        return {
            "intent": intent,
            "entities": [primary],
            "activities": activities,
            "message": assistant_message(content),
        }

    if intent == "risk_review":
        activities.append(activity("risk_check", "success", "Live execution is locked and deterministic risk controls are active."))
        content = (
            f"Risk review for {primary}: live trading remains locked, broker status is disconnected, "
            "and any future order intent must pass deterministic risk checks plus human approval."
        )
        return {
            "intent": intent,
            "entities": [primary],
            "activities": activities,
            "message": assistant_message(content),
        }

    if intent == "create_paper_order_intent":
        activities.append(activity("risk_check", "pending", "Paper order risk preview can be prepared, but no order was submitted."))
        return {
            "intent": intent,
            "entities": [primary],
            "activities": activities,
            "message": assistant_message(
                f"I can prepare a paper-trade idea for {primary}. It remains simulation-only and still needs risk sizing."
            ),
            "action": confirmation_action(
                f"Prepare paper order intent for {primary}",
                "This creates only a simulation intent after risk checks are connected.",
                "caution",
            ),
        }

    if intent == "create_live_order_intent":
        activities.append(activity("live_permission_gate", "blocked", "Live order submission is locked."))
        return {
            "intent": intent,
            "entities": [primary],
            "activities": activities,
            "message": assistant_message(
                "Live trading is still locked. I can research and prepare an intent only after production controls, broker configuration, risk checks, audit logging, and human approval are active."
            ),
            "action": confirmation_action(
                "Live action requires approval",
                "Live trading is blocked until the full production safety gate is configured.",
                "blocked",
            ),
        }

    return {
        "intent": intent,
        "entities": symbols,
        "activities": activities,
        "message": assistant_message(
            "The ATLAS backend is online. Ask for research, web search, a quote, a comparison, or risk review and I will use backend tools when available."
        ),
    }


class AtlasApiHandler(BaseHTTPRequestHandler):
    server_version = "ATLASLocalAPI/0.1"

    def do_OPTIONS(self) -> None:  # noqa: N802 - http.server API
        json_response(self, HTTPStatus.NO_CONTENT, {})

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        try:
            if path == "/health":
                json_response(self, HTTPStatus.OK, {"ok": True, "service": "atlas-backend"})
            elif path == "/status":
                json_response(self, HTTPStatus.OK, load_status())
            elif path == "/watchlist":
                json_response(self, HTTPStatus.OK, watchlist_payload())
            elif path.startswith("/market/quote/"):
                symbol = unquote(path.rsplit("/", 1)[-1])
                payload = quote_payload(symbol)
                json_response(self, HTTPStatus.OK if payload.get("available") else HTTPStatus.SERVICE_UNAVAILABLE, payload)
            elif path.startswith("/market/news/"):
                symbol = clean_symbol(unquote(path.rsplit("/", 1)[-1]))
                payload = web_search_payload(f"{symbol} stock latest news", int(query.get("limit", ["5"])[0]))
                json_response(self, HTTPStatus.OK if payload.get("available") else HTTPStatus.SERVICE_UNAVAILABLE, payload)
            elif path == "/web/search":
                search_query = query.get("q", [""])[0]
                limit = int(query.get("limit", ["5"])[0])
                payload = web_search_payload(search_query, limit)
                json_response(self, HTTPStatus.OK if payload.get("available") else HTTPStatus.SERVICE_UNAVAILABLE, payload)
            elif path == "/web/page":
                url = query.get("url", [""])[0]
                json_response(self, HTTPStatus.OK, webpage_payload(url))
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Unknown endpoint: {path}"})
        except Exception as error:  # pragma: no cover - defensive server boundary
            json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            payload = read_json(self)
            if path == "/assistant/turn":
                json_response(self, HTTPStatus.OK, assistant_turn(payload))
            else:
                json_response(self, HTTPStatus.NOT_FOUND, {"error": f"Unknown endpoint: {path}"})
        except Exception as error:  # pragma: no cover - defensive server boundary
            json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})

    def log_message(self, format: str, *args: Any) -> None:
        print(f"ATLAS API: {self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AtlasApiHandler)
    print(f"ATLAS backend listening on http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
