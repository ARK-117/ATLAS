import os
import json
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    import trafilatura
except ImportError:
    trafilatura = None

try:
    import yfinance as yf
except ImportError:
    yf = None

from atlas.trading import (
    AssetClass,
    JsonlAuditLogger,
    LiveBrokerNotConfiguredAdapter,
    MarketSnapshot,
    OrderIntent,
    OrderSide,
    PortfolioState,
    Position,
    RiskEngine,
    RiskPolicy,
    TradingGateway,
)


MODEL_NAME = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"

REPORTS_FOLDER = "reports"
AUDIT_FOLDER = "audit"
ORDER_INTENT_AUDIT_FILE = os.path.join(AUDIT_FOLDER, "order_intents.jsonl")
DATA_FILE = "atlas_data.json"

DEFAULT_DATA = {
    "paper_cash": 10000.0,
    "positions": {},
    "watchlist": [],
    "risk": {
        "max_trade_amount": 500.0,
        "max_total_exposure": 2000.0,
        "stop_loss_percent": 8.0,
        "take_profit_percent": 15.0
    }
}


def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def ask_atlas(prompt):
    if requests is None:
        return "The requests package is not installed. Install dependencies before using Ollama chat."

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def save_report(title, report):
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    safe_title = "".join(
        c for c in title.lower().replace(" ", "-")
        if c.isalnum() or c in "-_"
    )

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{safe_title}-{timestamp}.md"
    path = os.path.join(REPORTS_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(report)

    return path


def web_search(query, max_results=5):
    if DDGS is None:
        raise RuntimeError("The ddgs package is not installed.")

    results = []

    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", "")
            })

    return results


def read_webpage(url):
    if trafilatura is None:
        return ""

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""

        text = trafilatura.extract(downloaded)
        return text or ""
    except Exception:
        return ""


def research(topic):
    print("\nATLAS: Searching the web...")

    try:
        results = web_search(topic, max_results=5)
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return "I could not find web results."

    source_notes = []

    for index, result in enumerate(results, start=1):
        print(f"ATLAS: Reading source {index}: {result['title']}")

        page_text = read_webpage(result["url"])

        if not page_text:
            page_text = result["snippet"]

        source_notes.append(
            f"Source {index}\n"
            f"Title: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Content:\n{page_text[:3000]}\n"
        )

    combined_sources = "\n\n".join(source_notes)

    prompt = f"""
You are ATLAS, Automated Trading, Learning & Analysis System.

You are a practical Windows AI assistant focused on research, analysis, automation, and trading support.

Research topic:
{topic}

Use only the source notes below. Do not invent facts.

Create a useful report with these sections:
1. Quick Summary
2. Key Findings
3. Important Details
4. Risks / Things to Be Careful About
5. Final Conclusion
6. Sources Used with URLs

Source notes:
{combined_sources}
"""

    report = ask_atlas(prompt)
    path = save_report(topic, report)

    return f"{report}\n\nSaved report: {path}"


def get_stock_price(ticker):
    if yf is None:
        return None

    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="5d")

        if history.empty:
            return None

        return float(history["Close"].iloc[-1])
    except Exception:
        return None


def get_market_snapshot(ticker):
    if yf is None:
        return None

    ticker = ticker.upper().replace("$", "")

    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="5d")

        if history.empty:
            return None

        last_row = history.iloc[-1]
        last_index = history.index[-1]
        timestamp = last_index.to_pydatetime()

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            timestamp = timestamp.astimezone(timezone.utc)

        price = float(last_row["Close"])

        dollar_volumes = history["Close"] * history["Volume"]
        average_daily_dollar_volume = float(dollar_volumes.tail(5).mean())

        return MarketSnapshot(
            symbol=ticker,
            price=price,
            timestamp=timestamp,
            sector="unknown",
            asset_class=AssetClass.EQUITY,
            average_daily_dollar_volume=average_daily_dollar_volume,
            volatility_percent=0.0,
            source="yfinance-delayed-daily",
        )
    except Exception:
        return None


def stock_research(ticker):
    ticker = ticker.upper().replace("$", "")

    price = get_stock_price(ticker)

    query = (
        f"{ticker} stock latest news earnings financial performance "
        f"risks analyst discussion"
    )

    report = research(query)

    price_text = "Price unavailable."
    if price:
        price_text = f"Recent price from yfinance: {price:.2f}"

    final_report = (
        f"# ATLAS Stock Research: {ticker}\n\n"
        f"{price_text}\n\n"
        f"{report}\n\n"
        f"Note: This is research and analysis support, not guaranteed prediction."
    )

    path = save_report(f"stock-{ticker}", final_report)

    return f"{final_report}\n\nSaved stock report: {path}"


def add_watchlist(ticker):
    data = load_data()
    ticker = ticker.upper().replace("$", "")

    if ticker not in data["watchlist"]:
        data["watchlist"].append(ticker)
        save_data(data)
        return f"{ticker} added to watchlist."

    return f"{ticker} is already in your watchlist."


def show_watchlist():
    data = load_data()

    if not data["watchlist"]:
        return "Your watchlist is empty."

    lines = ["ATLAS Watchlist:"]

    for ticker in data["watchlist"]:
        price = get_stock_price(ticker)
        if price:
            lines.append(f"- {ticker}: {price:.2f}")
        else:
            lines.append(f"- {ticker}: price unavailable")

    return "\n".join(lines)


def total_exposure(data):
    total = 0.0

    for ticker, position in data["positions"].items():
        price = get_stock_price(ticker)
        if price:
            total += position["shares"] * price

    return total


def development_portfolio_state(data):
    positions = {}
    total_value = float(data["paper_cash"])

    for ticker, position in data["positions"].items():
        price = get_stock_price(ticker)
        if not price:
            continue

        live_position = Position(
            symbol=ticker,
            quantity=float(position["shares"]),
            market_price=price,
        )
        positions[ticker] = live_position
        total_value += live_position.market_value

    return PortfolioState(
        account_id="local-development",
        equity=max(total_value, 0.0),
        cash=float(data["paper_cash"]),
        positions=positions,
        peak_equity=max(total_value, 0.0),
    )


def default_live_risk_policy():
    return RiskPolicy()


def live_policy_summary():
    policy = default_live_risk_policy()

    return (
        "ATLAS live trading policy state:\n"
        f"- Live trading enabled: {policy.live_trading_enabled}\n"
        f"- Live Production Mode: {policy.live_production_mode}\n"
        f"- Permission level: L{int(policy.permission_level)} {policy.permission_level.name}\n"
        f"- Broker connection configured: {policy.broker_connection_configured}\n"
        f"- Secure secrets management confirmed: {policy.secure_secrets_management}\n"
        f"- User authenticated: {policy.user_authenticated}\n"
        f"- Role permission granted: {policy.role_permission_granted}\n"
        f"- Approval workflow enabled: {policy.approval_workflow_enabled}\n"
        f"- Broker status healthy: {policy.broker_status_healthy}\n"
        f"- Compliance checks passed: {policy.compliance_checks_passed}\n\n"
        "Default development mode blocks real broker execution. "
        "See docs/LIVE_TRADING_POLICY.md before enabling production controls."
    )


def create_order_intent(side_text, ticker, quantity_text, stop_loss_text, max_loss_text, reason):
    ticker = ticker.upper().replace("$", "")
    side_text = side_text.lower()

    try:
        side = OrderSide(side_text)
    except ValueError:
        return "Invalid side. Use buy or sell."

    try:
        quantity = float(quantity_text)
        stop_loss_price = float(stop_loss_text)
        expected_max_loss = float(max_loss_text)
    except ValueError:
        return "Invalid numeric value. Use: intent buy TICKER QTY STOP_LOSS EXPECTED_MAX_LOSS REASON"

    if quantity <= 0:
        return "Quantity must be greater than 0."

    if stop_loss_price <= 0:
        return "Stop-loss price must be greater than 0."

    if expected_max_loss <= 0:
        return "Expected maximum loss must be greater than 0."

    if not reason.strip():
        return "Reason is required for every real-trading order intent."

    market = get_market_snapshot(ticker)
    if not market:
        return "Could not create market snapshot. Order intent was not created."

    intent = OrderIntent(
        symbol=ticker,
        side=side,
        quantity=quantity,
        asset_class=AssetClass.EQUITY,
        stop_loss_price=stop_loss_price,
        expected_max_loss=expected_max_loss,
        reason=reason.strip(),
        data_sources_used=(market.source,),
        created_by="local-cli",
        strategy_id="manual-cli",
    )

    gateway = TradingGateway(
        risk_engine=RiskEngine(),
        broker=LiveBrokerNotConfiguredAdapter(),
        audit_logger=JsonlAuditLogger(ORDER_INTENT_AUDIT_FILE),
    )

    result = gateway.submit_intent(
        intent=intent,
        portfolio=development_portfolio_state(load_data()),
        market=market,
        policy=default_live_risk_policy(),
    )

    reason_lines = []
    if result.message:
        reason_lines = [f"- {item.strip()}" for item in result.message.split(";") if item.strip()]

    lines = [
        "ATLAS real-trading order intent risk check",
        f"Intent ID: {intent.id}",
        f"Symbol: {intent.symbol}",
        f"Side: {intent.side.value}",
        f"Quantity: {intent.quantity:g}",
        f"Reference price source: {market.source}",
        f"Reference price: ${market.price:.2f}",
        f"Market data timestamp UTC: {market.timestamp.isoformat()}",
        f"Estimated notional: ${intent.notional(market):.2f}",
        f"Expected max loss: ${intent.expected_max_loss:.2f}",
        f"Stop-loss price: ${intent.stop_loss_price:.2f}",
        f"Status: {result.status}",
        f"Accepted by execution gateway: {result.accepted}",
        f"Audit log: {ORDER_INTENT_AUDIT_FILE}",
    ]

    if reason_lines:
        lines.append("Blocking reasons:")
        lines.extend(reason_lines)

    lines.append(
        "No live broker order was placed. Live broker execution requires Live Production Mode, "
        "approved broker credentials, permissions, risk approval, audit logging, and human approval."
    )

    return "\n".join(lines)


def paper_buy(ticker, amount):
    data = load_data()
    risk = data["risk"]

    ticker = ticker.upper().replace("$", "")

    try:
        amount = float(amount)
    except ValueError:
        return "Invalid amount."

    if amount <= 0:
        return "Amount must be greater than 0."

    if amount > risk["max_trade_amount"]:
        return f"Blocked. Max trade amount is ${risk['max_trade_amount']:.2f}."

    if amount > data["paper_cash"]:
        return "Blocked. Not enough paper cash."

    current_exposure = total_exposure(data)

    if current_exposure + amount > risk["max_total_exposure"]:
        return f"Blocked. Max total exposure is ${risk['max_total_exposure']:.2f}."

    price = get_stock_price(ticker)

    if not price:
        return "Could not get stock price."

    shares = amount / price
    stop_loss_price = price * (1 - risk["stop_loss_percent"] / 100)
    take_profit_price = price * (1 + risk["take_profit_percent"] / 100)

    print("\nATLAS Paper Trade Preview")
    print(f"Ticker: {ticker}")
    print(f"Buy amount: ${amount:.2f}")
    print(f"Current price: ${price:.2f}")
    print(f"Paper shares: {shares:.6f}")
    print(f"Stop-loss simulation price: ${stop_loss_price:.2f}")
    print(f"Take-profit simulation price: ${take_profit_price:.2f}")
    print("\nThis is paper trading only, not real money.")

    confirm = input("Type CONFIRM to place this paper trade: ").strip()

    if confirm != "CONFIRM":
        return "Paper trade cancelled."

    if ticker not in data["positions"]:
        data["positions"][ticker] = {
            "shares": 0.0,
            "average_price": 0.0,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price
        }

    position = data["positions"][ticker]

    old_value = position["shares"] * position["average_price"]
    new_value = amount
    new_shares = position["shares"] + shares

    position["average_price"] = (old_value + new_value) / new_shares
    position["shares"] = new_shares
    position["stop_loss_price"] = stop_loss_price
    position["take_profit_price"] = take_profit_price

    data["paper_cash"] -= amount

    save_data(data)

    return f"Paper buy completed: {ticker}, ${amount:.2f}."


def portfolio():
    data = load_data()

    lines = []
    lines.append(f"Paper cash: ${data['paper_cash']:.2f}")
    lines.append("Positions:")

    if not data["positions"]:
        lines.append("- No positions.")
        return "\n".join(lines)

    total_value = data["paper_cash"]

    for ticker, position in data["positions"].items():
        price = get_stock_price(ticker)

        if not price:
            lines.append(f"- {ticker}: price unavailable")
            continue

        value = position["shares"] * price
        cost = position["shares"] * position["average_price"]
        pnl = value - cost
        total_value += value

        lines.append(
            f"- {ticker}: {position['shares']:.6f} shares | "
            f"Price: ${price:.2f} | "
            f"Value: ${value:.2f} | "
            f"P/L: ${pnl:.2f} | "
            f"Stop: ${position['stop_loss_price']:.2f} | "
            f"Target: ${position['take_profit_price']:.2f}"
        )

    lines.append(f"Total paper account value: ${total_value:.2f}")

    return "\n".join(lines)


def check_stops():
    data = load_data()

    if not data["positions"]:
        return "No paper positions to check."

    messages = []

    for ticker in list(data["positions"].keys()):
        position = data["positions"][ticker]
        price = get_stock_price(ticker)

        if not price:
            messages.append(f"{ticker}: price unavailable.")
            continue

        should_sell = False
        reason = ""

        if price <= position["stop_loss_price"]:
            should_sell = True
            reason = "stop-loss triggered"

        elif price >= position["take_profit_price"]:
            should_sell = True
            reason = "take-profit triggered"

        if should_sell:
            value = position["shares"] * price
            data["paper_cash"] += value
            del data["positions"][ticker]

            messages.append(
                f"{ticker}: paper sold at ${price:.2f}. "
                f"Reason: {reason}. Value returned: ${value:.2f}"
            )
        else:
            messages.append(
                f"{ticker}: no action. Current ${price:.2f}, "
                f"stop ${position['stop_loss_price']:.2f}, "
                f"target ${position['take_profit_price']:.2f}."
            )

    save_data(data)

    return "\n".join(messages)


def settings():
    data = load_data()
    risk = data["risk"]

    return (
        "ATLAS risk settings:\n"
        f"- Max trade amount: ${risk['max_trade_amount']:.2f}\n"
        f"- Max total exposure: ${risk['max_total_exposure']:.2f}\n"
        f"- Stop-loss percent: {risk['stop_loss_percent']:.2f}%\n"
        f"- Take-profit percent: {risk['take_profit_percent']:.2f}%"
    )


def help_menu():
    return """
ATLAS commands:

General chat:
  hello

Research:
  research best AI tools for Windows automation
  research current OLED monitor prices in Australia

Stock research:
  stock NVDA
  stock AAPL
  stock TSLA
  stock CBA.AX

Watchlist:
  watch NVDA
  watch CBA.AX
  watchlist

Paper trading:
  paper buy NVDA 100
  paper buy CBA.AX 100
  portfolio
  check stops

Real trading order intents:
  live policy
  intent buy NVDA 1 450 25 momentum thesis with stop defined
  intent sell NVDA 1 500 25 risk reduction thesis

Settings:
  settings

Exit:
  quit
"""


def main():
    print("ATLAS v1 is running.")
    print("ATLAS = Automated Trading, Learning & Analysis System")
    print(help_menu())

    while True:
        command = input("\nYou: ").strip()

        if not command:
            continue

        lower = command.lower()

        try:
            if lower in ["quit", "exit", "stop"]:
                print("ATLAS: Shutting down.")
                break

            elif lower.startswith("research "):
                topic = command[9:].strip()
                print("\nATLAS:\n")
                print(research(topic))

            elif lower.startswith("stock "):
                ticker = command[6:].strip()
                print("\nATLAS:\n")
                print(stock_research(ticker))

            elif lower.startswith("watch "):
                ticker = command[6:].strip()
                print("\nATLAS:")
                print(add_watchlist(ticker))

            elif lower == "watchlist":
                print("\nATLAS:\n")
                print(show_watchlist())

            elif lower.startswith("paper buy "):
                parts = command.split()

                if len(parts) != 4:
                    print("Use: paper buy TICKER AMOUNT")
                    continue

                ticker = parts[2]
                amount = parts[3]

                print("\nATLAS:\n")
                print(paper_buy(ticker, amount))

            elif lower == "live policy":
                print("\nATLAS:\n")
                print(live_policy_summary())

            elif lower.startswith("intent "):
                parts = command.split(maxsplit=6)

                if len(parts) != 7:
                    print("Use: intent buy TICKER QTY STOP_LOSS EXPECTED_MAX_LOSS REASON")
                    continue

                _, side, ticker, quantity, stop_loss, expected_max_loss, reason = parts

                print("\nATLAS:\n")
                print(create_order_intent(side, ticker, quantity, stop_loss, expected_max_loss, reason))

            elif lower == "portfolio":
                print("\nATLAS:\n")
                print(portfolio())

            elif lower == "check stops":
                print("\nATLAS:\n")
                print(check_stops())

            elif lower == "settings":
                print("\nATLAS:\n")
                print(settings())

            elif lower == "help":
                print(help_menu())

            else:
                prompt = f"""
You are ATLAS, Automated Trading, Learning & Analysis System.
You are a practical Windows AI assistant.

The user said:
{command}

Reply briefly and helpfully.
If the user wants research, tell them to use:
research [topic]

If the user wants stock research, tell them to use:
stock [ticker]
"""
                print("\nATLAS:\n")
                print(ask_atlas(prompt))

        except Exception as e:
            print("\nATLAS ERROR:")
            print(e)


if __name__ == "__main__":
    main()
