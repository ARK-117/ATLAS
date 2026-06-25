import os
import json
from datetime import datetime, timedelta, timezone

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
    Approval,
    AssetClass,
    JsonlAuditLogger,
    LiveBrokerNotConfiguredAdapter,
    MarketSnapshot,
    OrderIntent,
    OrderSide,
    OrderType,
    PortfolioState,
    Position,
    RiskEngine,
    RiskPolicy,
    RiskPolicyConfigError,
    TradingGateway,
    TimeInForce,
    list_risk_policy_profiles,
    load_risk_policy_profile,
    risk_policy_to_dict,
)


MODEL_NAME = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"

REPORTS_FOLDER = "reports"
AUDIT_FOLDER = "audit"
ORDER_INTENT_AUDIT_FILE = os.path.join(AUDIT_FOLDER, "order_intents.jsonl")
DATA_FILE = "atlas_data.json"
DEFAULT_RISK_POLICY_PROFILE = "development"
APPROVAL_CONFIRMATION = "APPROVE_LIVE_INTENT"

DEFAULT_DATA = {
    "paper_cash": 10000.0,
    "positions": {},
    "watchlist": [],
    "order_intents": {},
    "approvals": {},
    "active_risk_policy_profile": DEFAULT_RISK_POLICY_PROFILE,
    "risk": {
        "max_trade_amount": 500.0,
        "max_total_exposure": 2000.0,
        "stop_loss_percent": 8.0,
        "take_profit_percent": 15.0
    }
}


def fresh_default_data():
    return json.loads(json.dumps(DEFAULT_DATA))


def load_data():
    if not os.path.exists(DATA_FILE):
        data = fresh_default_data()
        save_data(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    changed = False
    for key, value in DEFAULT_DATA.items():
        if key not in data:
            data[key] = json.loads(json.dumps(value))
            changed = True

    if changed:
        save_data(data)

    return data


def save_data(data):
    data_dir = os.path.dirname(DATA_FILE)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def utc_now():
    return datetime.now(timezone.utc)


def parse_datetime(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
    profile_name = active_risk_policy_profile()

    try:
        return load_risk_policy_profile(profile_name)
    except RiskPolicyConfigError:
        return RiskPolicy()


def serialize_order_intent(intent):
    return {
        "id": intent.id,
        "symbol": intent.symbol,
        "side": intent.side.value,
        "quantity": intent.quantity,
        "asset_class": intent.asset_class.value,
        "order_type": intent.order_type.value,
        "time_in_force": intent.time_in_force.value,
        "limit_price": intent.limit_price,
        "stop_price": intent.stop_price,
        "estimated_fees": intent.estimated_fees,
        "expected_max_loss": intent.expected_max_loss,
        "stop_loss_price": intent.stop_loss_price,
        "invalidation_condition": intent.invalidation_condition,
        "reason": intent.reason,
        "data_sources_used": list(intent.data_sources_used),
        "uses_margin": intent.uses_margin,
        "leverage_multiplier": intent.leverage_multiplier,
        "is_autonomous": intent.is_autonomous,
        "strategy_id": intent.strategy_id,
        "created_by": intent.created_by,
        "created_at": intent.created_at.isoformat(),
    }


def deserialize_order_intent(raw):
    return OrderIntent(
        id=raw["id"],
        symbol=raw["symbol"],
        side=OrderSide(raw["side"]),
        quantity=float(raw["quantity"]),
        asset_class=AssetClass(raw.get("asset_class", AssetClass.EQUITY.value)),
        order_type=OrderType(raw.get("order_type", OrderType.MARKET.value)),
        time_in_force=TimeInForce(raw.get("time_in_force", TimeInForce.DAY.value)),
        limit_price=raw.get("limit_price"),
        stop_price=raw.get("stop_price"),
        estimated_fees=float(raw.get("estimated_fees", 0.0)),
        expected_max_loss=raw.get("expected_max_loss"),
        stop_loss_price=raw.get("stop_loss_price"),
        invalidation_condition=raw.get("invalidation_condition", ""),
        reason=raw.get("reason", ""),
        data_sources_used=tuple(raw.get("data_sources_used", ())),
        uses_margin=bool(raw.get("uses_margin", False)),
        leverage_multiplier=float(raw.get("leverage_multiplier", 1.0)),
        is_autonomous=bool(raw.get("is_autonomous", False)),
        strategy_id=raw.get("strategy_id", "manual"),
        created_by=raw.get("created_by", "user"),
        created_at=parse_datetime(raw["created_at"]),
    )


def serialize_market_snapshot(market):
    return {
        "symbol": market.symbol,
        "price": market.price,
        "timestamp": market.timestamp.isoformat(),
        "sector": market.sector,
        "asset_class": market.asset_class.value,
        "bid_ask_spread_percent": market.bid_ask_spread_percent,
        "average_daily_dollar_volume": market.average_daily_dollar_volume,
        "volatility_percent": market.volatility_percent,
        "is_halted": market.is_halted,
        "has_upcoming_earnings": market.has_upcoming_earnings,
        "has_major_unverified_news": market.has_major_unverified_news,
        "source": market.source,
    }


def deserialize_market_snapshot(raw):
    return MarketSnapshot(
        symbol=raw["symbol"],
        price=float(raw["price"]),
        timestamp=parse_datetime(raw["timestamp"]),
        sector=raw.get("sector", "unknown"),
        asset_class=AssetClass(raw.get("asset_class", AssetClass.EQUITY.value)),
        bid_ask_spread_percent=float(raw.get("bid_ask_spread_percent", 0.0)),
        average_daily_dollar_volume=float(raw.get("average_daily_dollar_volume", 0.0)),
        volatility_percent=float(raw.get("volatility_percent", 0.0)),
        is_halted=bool(raw.get("is_halted", False)),
        has_upcoming_earnings=bool(raw.get("has_upcoming_earnings", False)),
        has_major_unverified_news=bool(raw.get("has_major_unverified_news", False)),
        source=raw.get("source", "unknown"),
    )


def serialize_approval(approval):
    return {
        "order_intent_id": approval.order_intent_id,
        "approved_by": approval.approved_by,
        "approved_at": approval.approved_at.isoformat(),
        "expires_at": approval.expires_at.isoformat(),
        "production_acknowledged": approval.production_acknowledged,
    }


def deserialize_approval(raw):
    return Approval(
        order_intent_id=raw["order_intent_id"],
        approved_by=raw["approved_by"],
        approved_at=parse_datetime(raw["approved_at"]),
        expires_at=parse_datetime(raw["expires_at"]),
        production_acknowledged=bool(raw.get("production_acknowledged", False)),
    )


def store_order_intent_record(intent, market, result):
    data = load_data()
    data["order_intents"][intent.id] = {
        "intent": serialize_order_intent(intent),
        "market_snapshot": serialize_market_snapshot(market),
        "policy_profile": active_risk_policy_profile(),
        "last_status": result.status,
        "last_message": result.message,
        "broker_accepted": result.accepted,
        "created_at": intent.created_at.isoformat(),
        "updated_at": utc_now().isoformat(),
    }
    save_data(data)


def get_order_intent_record(intent_id):
    data = load_data()
    return data["order_intents"].get(intent_id)


def list_order_intents():
    data = load_data()
    records = list(data["order_intents"].values())

    if not records:
        return "No order intents recorded."

    records.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    lines = ["ATLAS order intents:"]

    for record in records[:20]:
        intent = record["intent"]
        lines.append(
            f"- {intent['id']} | {intent['side']} {intent['quantity']:g} "
            f"{intent['symbol']} | status {record['last_status']} | "
            f"profile {record['policy_profile']}"
        )

    return "\n".join(lines)


def show_order_intent(intent_id):
    record = get_order_intent_record(intent_id)
    if not record:
        return f"Order intent not found: {intent_id}"

    intent = record["intent"]
    market = record["market_snapshot"]
    approval = load_approval(intent_id)

    lines = [
        f"ATLAS order intent: {intent_id}",
        f"- Symbol: {intent['symbol']}",
        f"- Side: {intent['side']}",
        f"- Quantity: {intent['quantity']:g}",
        f"- Order type: {intent['order_type']}",
        f"- Time in force: {intent['time_in_force']}",
        f"- Expected max loss: {intent['expected_max_loss']}",
        f"- Stop-loss price: {intent['stop_loss_price']}",
        f"- Reason: {intent['reason']}",
        f"- Data sources: {', '.join(intent['data_sources_used'])}",
        f"- Reference price: {market['price']}",
        f"- Market timestamp UTC: {market['timestamp']}",
        f"- Policy profile: {record['policy_profile']}",
        f"- Last status: {record['last_status']}",
        f"- Broker accepted: {record['broker_accepted']}",
        f"- Last message: {record['last_message']}",
    ]

    if approval:
        lines.append(f"- Approval: recorded by {approval.approved_by}, expires {approval.expires_at.isoformat()}")
    else:
        lines.append("- Approval: none")

    return "\n".join(lines)


def load_approval(intent_id):
    data = load_data()
    raw = data["approvals"].get(intent_id)
    if not raw:
        return None
    return deserialize_approval(raw)


def approve_order_intent(intent_id, confirmation_text, approved_by="local-cli"):
    record = get_order_intent_record(intent_id)
    if not record:
        return f"Order intent not found: {intent_id}"

    if confirmation_text != APPROVAL_CONFIRMATION:
        return (
            f"Approval blocked. To approve this local order intent, use:\n"
            f"approve intent {intent_id} {APPROVAL_CONFIRMATION}"
        )

    now = utc_now()
    approval = Approval(
        order_intent_id=intent_id,
        approved_by=approved_by,
        approved_at=now,
        expires_at=now + timedelta(minutes=5),
        production_acknowledged=True,
    )

    data = load_data()
    data["approvals"][intent_id] = serialize_approval(approval)
    save_data(data)

    JsonlAuditLogger(ORDER_INTENT_AUDIT_FILE).append(
        "human_approval_recorded",
        {
            "order_intent_id": intent_id,
            "approved_by": approved_by,
            "approved_at": approval.approved_at.isoformat(),
            "expires_at": approval.expires_at.isoformat(),
            "production_acknowledged": approval.production_acknowledged,
        },
    )

    return (
        f"Approval recorded for order intent {intent_id}.\n"
        "This approval does not place a live broker order. Use recheck intent ID to rerun risk checks."
    )


def recheck_order_intent(intent_id):
    record = get_order_intent_record(intent_id)
    if not record:
        return f"Order intent not found: {intent_id}"

    intent = deserialize_order_intent(record["intent"])
    stored_market = deserialize_market_snapshot(record["market_snapshot"])
    market = get_market_snapshot(intent.symbol) or stored_market
    approval = load_approval(intent_id)

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
        approval=approval,
    )

    store_order_intent_record(intent, market, result)

    reason_lines = []
    if result.message:
        reason_lines = [f"- {item.strip()}" for item in result.message.split(";") if item.strip()]

    lines = [
        f"ATLAS order intent recheck: {intent_id}",
        f"Status: {result.status}",
        f"Accepted by execution gateway: {result.accepted}",
        f"Risk policy profile: {active_risk_policy_profile()}",
        f"Approval present: {approval is not None}",
        f"Audit log: {ORDER_INTENT_AUDIT_FILE}",
    ]

    if reason_lines:
        lines.append("Blocking reasons:")
        lines.extend(reason_lines)

    lines.append("No live broker order was placed.")
    return "\n".join(lines)


def active_risk_policy_profile():
    data = load_data()
    return data.get("active_risk_policy_profile", DEFAULT_RISK_POLICY_PROFILE)


def set_active_risk_policy_profile(profile_name):
    profile_name = profile_name.strip()
    profiles = list_risk_policy_profiles()

    if profile_name not in profiles:
        return (
            f"Unknown risk policy profile: {profile_name}\n"
            f"Available profiles: {', '.join(profiles) if profiles else 'none'}"
        )

    try:
        load_risk_policy_profile(profile_name)
    except RiskPolicyConfigError as error:
        return f"Risk policy profile is invalid: {error}"

    data = load_data()
    data["active_risk_policy_profile"] = profile_name
    save_data(data)

    return f"Active risk policy profile set to: {profile_name}"


def policy_profile_list():
    profiles = list_risk_policy_profiles()
    active_profile = active_risk_policy_profile()

    if not profiles:
        return "No risk policy profiles found."

    lines = ["ATLAS risk policy profiles:"]
    for profile in profiles:
        marker = "*" if profile == active_profile else "-"
        lines.append(f"{marker} {profile}")

    return "\n".join(lines)


def policy_profile_detail(profile_name=None):
    profile_name = profile_name or active_risk_policy_profile()

    try:
        policy = load_risk_policy_profile(profile_name)
    except RiskPolicyConfigError as error:
        return f"Could not load risk policy profile: {error}"

    policy_dict = risk_policy_to_dict(policy)
    lines = [f"ATLAS risk policy profile: {profile_name}"]
    for key in sorted(policy_dict):
        lines.append(f"- {key}: {policy_dict[key]}")

    return "\n".join(lines)


def live_policy_summary():
    profile_name = active_risk_policy_profile()
    policy = default_live_risk_policy()

    return (
        "ATLAS live trading policy state:\n"
        f"- Active profile: {profile_name}\n"
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
        "Use policy profiles to inspect or switch local risk profiles. "
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
    store_order_intent_record(intent, market, result)

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
        f"Risk policy profile: {active_risk_policy_profile()}",
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
  policy profiles
  policy show
  policy show paper
  policy use paper
  intent buy NVDA 1 450 25 momentum thesis with stop defined
  intent sell NVDA 1 500 25 risk reduction thesis
  intents
  intent show INTENT_ID
  approve intent INTENT_ID APPROVE_LIVE_INTENT
  recheck intent INTENT_ID

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

            elif lower == "policy profiles":
                print("\nATLAS:\n")
                print(policy_profile_list())

            elif lower == "policy show":
                print("\nATLAS:\n")
                print(policy_profile_detail())

            elif lower.startswith("policy show "):
                profile_name = command[12:].strip()
                print("\nATLAS:\n")
                print(policy_profile_detail(profile_name))

            elif lower.startswith("policy use "):
                profile_name = command[11:].strip()
                print("\nATLAS:\n")
                print(set_active_risk_policy_profile(profile_name))

            elif lower == "intents":
                print("\nATLAS:\n")
                print(list_order_intents())

            elif lower.startswith("intent show "):
                intent_id = command[12:].strip()
                print("\nATLAS:\n")
                print(show_order_intent(intent_id))

            elif lower.startswith("intent "):
                parts = command.split(maxsplit=6)

                if len(parts) != 7:
                    print("Use: intent buy TICKER QTY STOP_LOSS EXPECTED_MAX_LOSS REASON")
                    continue

                _, side, ticker, quantity, stop_loss, expected_max_loss, reason = parts

                print("\nATLAS:\n")
                print(create_order_intent(side, ticker, quantity, stop_loss, expected_max_loss, reason))

            elif lower.startswith("approve intent "):
                parts = command.split(maxsplit=3)

                if len(parts) != 4:
                    print(f"Use: approve intent INTENT_ID {APPROVAL_CONFIRMATION}")
                    continue

                _, _, intent_id, confirmation = parts
                print("\nATLAS:\n")
                print(approve_order_intent(intent_id, confirmation))

            elif lower.startswith("recheck intent "):
                intent_id = command[15:].strip()
                print("\nATLAS:\n")
                print(recheck_order_intent(intent_id))

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
