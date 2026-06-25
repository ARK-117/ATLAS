# ATLAS Professional AI Research and Trading System Blueprint

ATLAS stands for Automated Trading, Learning, and Analysis System. The current `app.py` is a useful prototype: it performs web research, calls a local Ollama model, tracks a watchlist, performs simple stock lookup, and simulates paper buys with basic exposure, stop-loss, and take-profit checks.

This blueprint describes the production architecture that should grow around that prototype. The target system is a real-money research and trading platform, not a paper-trading toy. The core rule is simple: ATLAS may miss opportunities, but it must never ignore safety, legality, risk limits, data integrity, auditability, or human control.

This document is technical planning and risk-control guidance. It is not legal, tax, accounting, brokerage, or personalized financial advice. Before live trading, consult qualified legal, compliance, tax, and brokerage professionals.

## 1. Product Boundary

ATLAS should be built as a modular AI operating system where real trading is one permissioned module.

Default capabilities:

- Research public market data.
- Summarize filings, earnings, news, macro data, sector trends, and technical conditions.
- Generate clearly labeled research opinions and real trade candidates.
- Backtest, stress test, and paper-trade strategies before production approval.
- Monitor portfolio risk in simulation and live broker-connected environments.
- Produce explainable reports with uncertainty and source quality.

Production trading capabilities:

- Real broker account connection.
- Real order-intent creation.
- Real order submission after deterministic risk checks and human approval.
- Real position, cash, exposure, and P/L reconciliation.
- Real-time shutdown controls and broker-state monitoring.

Disabled unless explicitly enabled through a protected production process:

- Withdrawals or cash movement.
- Broker setting changes.
- Margin, leverage, short selling, options, futures, crypto, or complex orders.
- Autonomous execution without human approval and signed production approval.
- Any use of insider, stolen, hacked, leaked, or non-public material.

## 2. System Principles

- Research, opinion, simulation, order intent, and live action must be separate object types in the database and UI.
- LLMs can propose and explain; deterministic services must validate, size, block, route, and audit.
- Trading tools must be isolated from research tools by separate credentials and permissions.
- Broker credentials must never be exposed to prompts, chat logs, reports, or front-end clients.
- Every sensitive decision must produce an immutable audit trail.
- Missing data, stale data, conflicting data, or model uncertainty must reduce risk or block action.
- Fail-closed behavior is mandatory. When unsure, pause.
- Live trading is the production target, but it requires an explicit production configuration, hardened deployment, risk approval, and a human approval workflow.

## 3. High-Level Architecture

Recommended production layout:

- Frontend: Next.js or React dashboard for research, portfolio, risk, approvals, backtests, paper trading, alerts, and admin controls.
- API gateway: FastAPI service with auth, rate limits, request validation, and role-based access control.
- Agent orchestrator: Coordinates research, analysis, portfolio, backtest, and reporting agents.
- Data ingestion services: Pull and stream market, fundamental, macro, news, filing, and alternative data.
- Data quality service: Validates freshness, schema, corporate actions, splits, duplicates, outliers, and source conflicts.
- Feature store: Stores point-in-time model features with versioning.
- Research store: Stores documents, filings, news, transcripts, analyst notes, embeddings, and citations.
- Strategy lab: Backtesting, walk-forward testing, parameter search, and model evaluation.
- Paper trading engine: Simulates orders, fills, slippage, fees, borrow constraints, and risk events.
- Portfolio/risk engine: Enforces all risk rules before any recommendation or order.
- Execution gateway: Broker adapter layer. No LLM direct access.
- Approval service: Human approval, two-person review for high-risk actions, and signed approval records.
- Audit log service: Append-only event log for data, prompts, model outputs, risk checks, approvals, and orders.
- Monitoring and alerting: Metrics, logs, traces, model drift, data feed health, broker status, and kill-switch state.

## 4. Recommended Technology Stack

MVP stack:

- Language: Python 3.12+.
- API: FastAPI, Pydantic, SQLAlchemy, Alembic.
- CLI: Typer or Click.
- Database: PostgreSQL.
- Cache and queues: Redis.
- Task worker: Celery, Dramatiq, or RQ for MVP.
- Market data prototype: yfinance only for early non-production experiments; replace with licensed vendors for serious use.
- Research model: local Ollama for private prototype tasks plus a high-quality hosted LLM for production-grade reasoning where allowed.
- Vector search: pgvector inside PostgreSQL for MVP.
- Backtesting: vectorbt, backtrader, Zipline Reloaded, or a custom event-driven engine once requirements mature.
- Dashboard: Streamlit for early internal tools or Next.js for production.
- Secrets: environment variables for local dev; cloud secret manager in staging/production.

Institutional stack:

- API: FastAPI services behind an API gateway.
- Databases: PostgreSQL for core objects, TimescaleDB or ClickHouse for time-series data, S3-compatible object storage for raw data, and Redis for cache/locks.
- Streaming: Kafka or Redpanda for market-data/event pipelines.
- Vector database: pgvector for integrated retrieval; Qdrant, Weaviate, Pinecone, or Milvus if vector workload grows beyond Postgres.
- Feature store: Feast or custom point-in-time feature tables.
- Orchestration: Prefect, Dagster, or Airflow.
- Containers: Docker.
- Runtime: Kubernetes only after the system needs horizontal scaling; otherwise start with a simpler VM/container deployment.
- Monitoring: Prometheus, Grafana, OpenTelemetry, Loki or ELK, Sentry, PagerDuty/Opsgenie.
- Security: Vault, AWS Secrets Manager, GCP Secret Manager, or Azure Key Vault.
- CI/CD: GitHub Actions with linting, tests, secret scanning, dependency scanning, and protected environments.

Official references used for stack and data planning:

- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- FRED API: https://fred.stlouisfed.org/docs/api/fred/
- Alpaca Market Data API: https://docs.alpaca.markets/us/docs/about-market-data-api
- Alpaca Paper Trading: https://docs.alpaca.markets/us/docs/paper-trading
- Alpaca Trading API: https://docs.alpaca.markets/us/docs/trading-api
- FINRA Rule 3110, Supervision: https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110
- FINRA Rule 2210, Communications with the Public: https://www.finra.org/rules-guidance/rulebooks/finra-rules/2210
- SEC Regulation Best Interest: https://www.sec.gov/rules-regulations/2019/06/regulation-best-interest-broker-dealer-standard-conduct
- PostgreSQL: https://www.postgresql.org/docs/current/
- pgvector: https://github.com/pgvector/pgvector
- Apache Kafka: https://kafka.apache.org/intro/
- Redis: https://redis.io/docs/latest/develop/

## 5. Data Sources

Use licensed, reliable, timestamped sources. Track source, retrieval time, licensing status, and data confidence for every record.

Market data:

- Real-time and historical equities: Polygon/Massive, Alpaca, Nasdaq Data Link, Databento, Tiingo, IEX Cloud alternatives, Bloomberg, Refinitiv, FactSet, or ICE depending on budget and licensing.
- Bars: 1 minute, 5 minute, daily, weekly, monthly.
- Quotes: bid, ask, spread, depth if available.
- Trades: price, size, exchange, conditions.
- Corporate actions: splits, dividends, mergers, symbol changes.
- Short interest, borrow availability, and fails-to-deliver if shorting is ever enabled.

Fundamentals:

- SEC EDGAR submissions and XBRL company facts for 10-K, 10-Q, 8-K, 20-F, 40-F, and related filings.
- Vendor-normalized fundamentals from Financial Modeling Prep, Intrinio, FactSet, Refinitiv, S&P Capital IQ, or Bloomberg when budget allows.
- Analyst estimates and revisions from licensed vendors only.

Macroeconomic data:

- FRED and ALFRED for rates, inflation, labor, money supply, recession indicators, yield curves, credit spreads, and real-time vintage analysis.
- Treasury, BLS, BEA, Census, IMF, World Bank, ECB, and central bank calendars.

News and sentiment:

- Licensed financial news: Dow Jones, Bloomberg, Benzinga, MT Newswires, RavenPack, Refinitiv, or similar.
- Public web/news search for research only, with source quality labels.
- Social sentiment is low trust by default and must never drive trades alone.

Institutional flows and market structure:

- 13F filings, insider Form 3/4/5 filings, ETF holdings, fund flows, options flow if licensed, dark pool/ATS data if licensed and understood.
- Treat all flow data as delayed, incomplete, and contextual rather than predictive certainty.

Alternative data:

- Web traffic, app rankings, credit card panels, satellite, shipping, hiring, job postings, pricing, supply chain, or geolocation data only if lawfully sourced, properly licensed, privacy-reviewed, and compliant.

## 6. Data Pipeline

Ingestion flow:

1. Connector fetches or streams source data.
2. Raw payload is stored unchanged in object storage with source metadata.
3. Parser normalizes data into canonical schemas.
4. Data quality service checks timestamp, schema, nulls, duplicates, outliers, corporate actions, and source conflicts.
5. Validated records are written to time-series tables and document tables.
6. Feature jobs create point-in-time features.
7. Embedding jobs index research documents into the vector store.
8. Event bus publishes update events to agents and dashboards.

Data quality rules:

- Reject market data with stale timestamps beyond configured threshold.
- Flag price moves that exceed volatility-based bands unless confirmed by multiple sources.
- Block trading decisions if primary and backup feeds disagree beyond tolerance.
- Store all data in UTC plus exchange-local calendar context.
- Preserve point-in-time history. Do not overwrite past values without versioning.
- Maintain corporate-action-adjusted and raw price series separately.
- Do not use revised macro/fundamental data for historical tests unless the revision date was known at the test timestamp.

## 7. Database Design

Core PostgreSQL tables:

- users, roles, permissions.
- portfolios, accounts, broker_connections.
- instruments, exchanges, trading_calendars.
- market_bars, market_quotes, market_trades.
- corporate_actions, dividends, splits.
- filings, filing_sections, xbrl_facts.
- news_articles, transcripts, analyst_notes.
- macro_series, macro_observations, macro_vintages.
- watchlists, research_requests, research_reports.
- trade_ideas, idea_evidence, idea_risk_checks.
- strategies, strategy_versions, strategy_parameters.
- backtest_runs, backtest_trades, backtest_metrics.
- paper_orders, paper_fills, paper_positions.
- live_order_intents, approvals, broker_orders, broker_fills.
- risk_limits, risk_events, shutdown_events.
- model_runs, prompts, tool_calls, citations.
- audit_events.

Time-series storage:

- PostgreSQL partitions or TimescaleDB for MVP.
- ClickHouse for high-volume tick/quote/event analytics.
- Object storage for raw vendor files and replayable event snapshots.

Vector storage:

- Use pgvector initially so documents, metadata, permissions, and embeddings remain near the relational data.
- Store embeddings for filings, transcripts, news, reports, strategy notes, and user-approved memory.
- Keep vector rows permission-scoped. A retrieval query must filter by user, portfolio, module, document type, confidentiality, and allowed tools before nearest-neighbor search.

## 8. Memory System

Use four separate memory classes:

- Working memory: Current task context. Short lived. Not persisted unless needed for audit.
- Research memory: Source-grounded facts, citations, summaries, and extracted entities.
- Portfolio memory: Positions, limits, strategy state, approvals, orders, and risk events.
- User preference memory: Approved preferences such as reporting format, watchlist, risk tolerance labels, and notification preferences.

Memory restrictions:

- Do not store API keys, broker credentials, government IDs, bank details, private documents, or sensitive personal information in LLM memory.
- All memory writes require type, source, timestamp, owner, sensitivity, retention period, and deletion policy.
- User can inspect, export, disable, or delete non-audit memory.
- Audit records are immutable and have separate retention rules.

## 9. Agent Architecture

Use specialized agents with least privilege:

- Router agent: Classifies user intent and assigns modules.
- Research agent: Searches filings, news, macro, and documents. No trading permission.
- Fundamental analyst agent: Revenue, margins, balance sheet, valuation, estimates, filings, and earnings calls.
- Technical analyst agent: Trend, momentum, volatility, volume, support/resistance, regime, and signal quality.
- Macro analyst agent: Rates, inflation, growth, liquidity, credit, central bank events, and sector sensitivity.
- News/sentiment analyst agent: Source quality, recency, event extraction, contradiction checks, and rumor rejection.
- Portfolio analyst agent: Current exposure, correlation, drawdown, concentration, liquidity, and scenario impact.
- Strategy agent: Converts hypotheses into testable strategy definitions.
- Backtest agent: Runs tests and reports metrics. Cannot approve live trading.
- Risk manager agent: Deterministic risk engine plus explanatory layer.
- Compliance agent: Checks policy, restricted lists, disclosures, source legality, and communication labels.
- Execution agent: Creates order intents only after policy and human approval. It cannot bypass risk checks.
- General assistant agent: Coding, document analysis, planning, email/calendar, browser, reporting, and business operations modules.

Agent workflow for a trade idea:

1. User requests research or the scanner finds a candidate.
2. Research agent gathers source-grounded evidence.
3. Fundamental, technical, macro, news, and portfolio agents score independent dimensions.
4. Strategy agent forms a hypothesis with entry, exit, invalidation, expected holding period, and data requirements.
5. Backtest service tests the hypothesis with realistic costs and point-in-time data.
6. Risk engine calculates position size, exposure impact, liquidity risk, drawdown impact, and event restrictions.
7. Compliance agent labels output as research/opinion/simulation and checks restricted content.
8. ATLAS produces a trade idea, not an order, with confidence, risk, evidence, downside, and why it may fail.
9. If live trading is enabled, user may request an order intent.
10. Approval service requires human confirmation.
11. Execution gateway re-checks risk and sends order to broker.
12. Audit service records every input, output, approval, and broker response.

## 10. Model Selection

Use a model router rather than one model for everything.

Recommended model roles:

- Fast local model: Command routing, basic summaries, offline private notes, and cheap classification.
- Strong hosted reasoning model: Complex research synthesis, multi-document reasoning, strategy critique, and report generation.
- Embedding model: Retrieval over filings, news, transcripts, research notes, and memory.
- Small classifier models: Sentiment, event detection, ticker/entity linking, source quality, and compliance labels.
- Traditional ML models: Forecasting, regime classification, anomaly detection, volatility prediction, and factor models.
- Deterministic code: Risk rules, sizing, order validation, accounting, data quality, and audit logging.

Model rules:

- The LLM must never invent prices, financial statements, news, ratings, or data.
- All market facts in outputs need data source, timestamp, and confidence.
- Every model run stores prompt template version, model name, parameters, tool calls, citations, and output hash.
- Use temperature near 0 for risk, compliance, extraction, and order-related workflows.
- Require source-grounded retrieval for financial claims.
- Run adversarial prompts and hallucination tests before enabling any model in production.

## 11. Research Output Standard

Every stock research report should include:

- Ticker, company, exchange, sector, industry, market cap, liquidity, and data timestamp.
- Current price source and freshness.
- Business summary and revenue drivers.
- Fundamental snapshot: growth, margins, cash flow, leverage, valuation, and earnings revisions if available.
- Technical snapshot: trend, momentum, volatility, volume, drawdown, support/resistance, and regime.
- Macro sensitivity: rates, inflation, dollar, commodities, credit, sector rotation.
- News and events: source quality, recency, materiality, and contradictions.
- Institutional/flow context if available and licensed.
- Bull case, bear case, base case.
- What would invalidate the thesis.
- Confidence score with explanation.
- Risk score with explanation.
- Portfolio impact.
- Clear label: research only, simulated idea, or order intent.

Confidence score should combine:

- Data quality.
- Source agreement.
- Recency.
- Model agreement.
- Backtest robustness.
- Liquidity.
- Regime fit.
- Event risk.

Confidence is not probability of profit. It is a quality-of-evidence score.

## 12. Feature Engineering

Price and technical features:

- Returns over multiple horizons.
- Moving averages and distance from moving averages.
- Realized volatility, ATR, beta, downside volatility.
- Momentum, trend strength, RSI, MACD, Bollinger bands.
- Volume z-score, dollar volume, turnover, gap size.
- Drawdown from recent highs.
- Relative strength versus sector, industry, and index.

Fundamental features:

- Revenue growth, EPS growth, gross/operating/net margins.
- Free cash flow margin and conversion.
- Debt/equity, net debt/EBITDA, interest coverage.
- ROIC, ROE, asset turnover.
- Valuation: P/E, EV/EBITDA, EV/Sales, P/B, FCF yield.
- Estimate revisions and earnings surprise where licensed.
- Filing-derived risk factor changes.

Macro features:

- Yield curve level and slope.
- Fed funds expectations if licensed.
- Inflation, unemployment, PMI, credit spreads.
- Dollar index, oil, gold, VIX, sector rotation.
- Macro release calendar and event windows.

News and NLP features:

- Material event type: earnings, guidance, M&A, lawsuit, regulation, product, management, cyber, financing.
- Sentiment with source quality weighting.
- Novelty versus previously known news.
- Contradiction score across sources.
- Filing section embeddings and risk-factor deltas.

Portfolio features:

- Current weight.
- Sector and factor exposure.
- Correlation to current holdings.
- Marginal contribution to volatility.
- Liquidity capacity.
- Scenario loss under stress.

Feature engineering rules:

- Features must be computed point-in-time.
- No look-ahead data.
- No survivorship-biased universes.
- Store feature version and code version.
- Keep raw, adjusted, and derived data separate.

## 13. Backtesting Engine

Start with a simple event-driven engine, then harden it.

Minimum components:

- Data loader with point-in-time universe.
- Exchange calendar and market hours.
- Signal generator.
- Portfolio/accounting engine.
- Commission and fee model.
- Slippage and spread model.
- Corporate actions support.
- Order model: market, limit, stop, stop-limit, bracket in simulation.
- Fill model with partial fills and liquidity caps.
- Risk engine integration.
- Metrics engine.
- Report generator.

Required metrics:

- CAGR, total return, volatility.
- Sharpe, Sortino, Calmar.
- Max drawdown, average drawdown, drawdown duration.
- Win rate, profit factor, expectancy.
- Average winner/loser.
- Turnover, fees, slippage, capacity.
- Exposure by sector, asset, factor, and strategy.
- Daily/weekly/monthly loss distribution.
- Tail losses, VaR/CVaR for analysis only.
- Benchmark-relative return and beta.

Backtesting protections:

- Use delisted names where possible.
- Use point-in-time fundamentals.
- Include realistic commissions, spreads, slippage, market impact, and borrow/financing costs.
- Do not optimize on the test set.
- Track all failed experiments to reduce cherry-picking.
- Prefer simple robust strategies over overfit parameter sets.

## 14. Strategy Validation

A strategy may move through gates only in this order:

1. Hypothesis documented before testing.
2. Historical backtest passes minimum risk-adjusted thresholds.
3. Sensitivity analysis shows no single parameter causes all performance.
4. Out-of-sample test passes.
5. Walk-forward test passes.
6. Stress tests pass.
7. Paper trading passes for a minimum observation window.
8. Live small-capital test passes.
9. Scale only after review.

Testing stages:

- Historical backtest: Broad first filter.
- Out-of-sample test: Hold back recent data or separate regimes.
- Walk-forward test: Refit only on past windows and test on future windows.
- Monte Carlo: Randomize trade order and returns to estimate drawdown risk.
- Transaction cost stress: Double or triple costs.
- Slippage stress: Wider spreads, delayed fills, partial fills.
- Regime stress: 2008, 2020, inflation/rate shock, sector crash, flash crash periods where data is available.
- Paper trading: Validate live data, clock sync, orders, cancels, errors, and monitoring.
- Small-capital live: Only after explicit enablement and approval.

Promotion rule:

- A strategy cannot be promoted because it "looks good." It must pass documented gates and receive human approval.

## 15. Paper Trading

Paper trading should be treated as a production rehearsal, not proof of profitability.

Paper engine must simulate:

- Slippage.
- Spread crossing.
- Partial fills.
- Liquidity limits.
- Fees.
- Corporate actions.
- Trading halts.
- Missing data.
- Order rejections.
- Network failures.
- Market open/close behavior.

Broker paper trading:

- Alpaca provides a real-time paper environment, but paper trading is still a simulation and does not fully account for market impact, information leakage, latency slippage, order queue position, price improvement, regulatory fees, or dividends. ATLAS must account for these gaps in its own reports.

Paper trading pass criteria:

- No policy violations.
- No unexplained orders.
- No stale data decisions.
- No broken audit records.
- Drawdown within limits.
- Slippage assumptions reasonable.
- Risk engine blocks expected test violations.
- Human approval flow works in rehearsal.

## 16. Broker Integration

Broker integration must be isolated behind an execution gateway.

Recommended broker adapter pattern:

- `BrokerAdapter` interface: accounts, positions, buying power, orders, cancels, fills, clock, assets, market calendar.
- `PaperBrokerAdapter`: internal simulator.
- `AlpacaPaperAdapter`: external paper trading.
- `AlpacaLiveAdapter`: disabled until production approval.
- `InteractiveBrokersAdapter`: future advanced adapter if needed.

Hard rule:

- The LLM can never directly call broker APIs.
- The LLM can request an order intent object.
- The risk engine and approval service decide whether the intent can become an order.

Order state machine:

- proposed -> risk_checked -> awaiting_approval -> approved -> final_risk_check -> submitted -> acknowledged -> partially_filled -> filled/cancelled/rejected -> reconciled.

Required live order pre-checks:

- Trading mode is live-enabled.
- User is authenticated.
- Human approval is fresh.
- Strategy is approved.
- Instrument is allowed.
- Market is open or extended hours allowed.
- Data is fresh.
- Price is within sanity bands.
- Spread and liquidity pass.
- Earnings/news restrictions pass.
- Position sizing passes.
- Portfolio exposure passes.
- Daily/weekly/monthly loss limits pass.
- Broker account state passes.
- Kill switch is not active.

## 17. Risk Management Rules

Use deterministic risk rules stored in database configuration and versioned.

Baseline default limits for early live testing, if ever enabled:

- Live trading: disabled.
- Allowed assets: liquid listed equities and ETFs only.
- Leverage: 1.0x max.
- Options/futures/crypto/short selling: disabled.
- Max risk per trade: 0.25% to 0.50% of account equity.
- Max position market value: 2% to 5% of account equity.
- Max single-name exposure: 5%.
- Max sector exposure: 20%.
- Max strategy exposure: 20%.
- Max total gross exposure: 80% to 100% for long-only early system.
- Max daily realized loss: 1%.
- Max weekly realized loss: 2%.
- Max monthly drawdown: 4%.
- Hard max drawdown from peak equity: 8% to 10%, then shutdown and review.
- Minimum average daily dollar volume: configurable, for example 50x intended order size.
- Maximum participation rate: configurable, for example 1% to 5% of average daily volume for small accounts; lower for larger accounts.
- Maximum bid-ask spread: configurable by price and liquidity bucket.

Position sizing:

- Use the smaller of exposure-based size and risk-based size.
- Risk-based shares = allowed dollar risk / absolute(entry price - stop price).
- Allowed dollar risk = account equity x risk_per_trade.
- Apply liquidity cap, sector cap, asset cap, strategy cap, and cash cap.
- Round down, never up.

Stop-loss logic:

- Every trade idea must include invalidation conditions.
- Stops can be technical, volatility-based, or thesis-based.
- For live trading, stop logic must be represented as monitored risk state, not just prose.
- If hard stop orders are used, consider gap risk, stop-market slippage, and stop-limit non-fill risk.
- If virtual stops are used, monitoring uptime and kill-switch procedures must be strong.

Take-profit logic:

- Use defined exit rules before entry.
- Examples: target multiple of risk, trailing stop, time stop, valuation target, earnings/event exit, or signal reversal.
- Partial profit-taking is allowed only if tested and documented.

Portfolio exposure:

- Calculate exposures before recommendation and before order submission.
- Include pending orders.
- Include correlated exposures and ETF look-through where data is available.
- Block trades that increase concentration beyond limits.

Liquidity checks:

- Minimum price.
- Minimum average daily volume and dollar volume.
- Maximum spread.
- Maximum order size as percentage of ADV and visible liquidity.
- Avoid low-float, halted, hard-to-borrow, or abnormal-volume names unless explicitly approved for research only.

Volatility checks:

- Block new positions when realized volatility exceeds configured threshold.
- Reduce size when ATR or intraday range is unusually high.
- Block after extreme one-day gap unless event has been verified and strategy permits it.

News and event restrictions:

- No new trade within configured window before earnings unless explicitly allowed.
- No new trade immediately after earnings until spread, volume, and price stabilize.
- Restrict trading around FOMC, CPI, jobs reports, major regulatory decisions, index rebalances, and company-specific material news.
- Block trading on unverified rumors, social hype, or suspicious spikes.

Emergency shutdown triggers:

- Daily/weekly/monthly loss limit breached.
- Max drawdown breached.
- Data feed stale or conflicting.
- Broker API unavailable or returning inconsistent state.
- Unexpected live order.
- Order submitted without approval.
- Missing audit log write.
- Model hallucination detected on required data.
- Unusual account activity.
- Position not reconciled.
- Repeated order rejection.
- Manual kill switch activated.

Shutdown behavior:

- Disable new order intents.
- Cancel open orders if policy requires and broker state is reliable.
- Alert user and admin.
- Snapshot account, positions, logs, data feed state, and model outputs.
- Require human review and signed restart approval.

## 18. Compliance and Legal Controls

Important:

- If ATLAS gives personalized advice to others, manages money, executes trades for others, markets performance, or operates as part of a business, it may trigger investment adviser, broker-dealer, commodity, privacy, advertising, recordkeeping, and supervision obligations. Get counsel before any external use.

Controls:

- Label every output: research, opinion, simulation, order intent, or executed order.
- Include no-guarantee and uncertainty language in financial outputs.
- Keep records of prompts, data, sources, model outputs, approvals, and actions.
- Maintain written supervisory procedures before production use in a regulated setting.
- Review public-facing communications and performance claims.
- Do not present backtest results as expected live performance.
- Maintain restricted lists and blocked securities if applicable.
- Detect and refuse market manipulation, insider information, wash trading, spoofing, pump-and-dump, coordinated buying, fake news, or misleading content.
- Review licensing for every data vendor.
- Keep customer/user data private and permission-scoped.

Human approval layer:

- Required for live trading.
- Required for changing risk settings.
- Required for broker connection.
- Required for withdrawals or cash movement if those features are ever added.
- Required for deleting logs.
- Required for enabling autonomous workflows.
- Required for memory writes containing sensitive or long-lived personal information.

Approval record must include:

- User identity.
- Timestamp.
- Requested action.
- Risk summary.
- Data timestamp.
- Strategy version.
- Position size.
- Expected portfolio impact.
- Warnings.
- Approval text or signed challenge.
- Resulting broker order ID if submitted.

## 19. Security

Security model:

- Least privilege for all services and tools.
- Separate read-only research credentials from broker trading credentials.
- No withdrawal permissions in ATLAS.
- No broker credentials in prompts or logs.
- No secrets in repository.
- MFA on broker, GitHub, cloud, and admin accounts.
- IP allowlists where supported.
- Secret rotation.
- Encryption in transit and at rest.
- Role-based access control.
- Admin actions require stronger authentication.
- Dependency scanning and secret scanning in CI.
- Regular backups and restore tests.

Prompt/tool security:

- Tool calls must be allowlisted.
- Retrieval must filter by permission before embedding similarity.
- System safety rules cannot be overwritten by user prompts.
- Model outputs are untrusted until validated.
- Prompt injection from webpages, filings, email, or documents must be detected and sandboxed.
- Browser automation and email/calendar modules must not have trading permissions.

## 20. Logging and Audit

Log levels:

- Operational logs: service health, errors, latency.
- Data logs: source, retrieval time, checksum, validation status.
- Model logs: model, prompt version, tools, citations, output hash.
- Risk logs: rules evaluated, pass/fail, limits, decision.
- Approval logs: approver, timestamp, action, warning text.
- Trading logs: order intent, broker request, broker response, fills, cancels, reconciliation.
- Security logs: login, permission changes, secret access, failed auth, admin actions.

Audit requirements:

- Append-only audit table or event stream.
- Tamper-evident hashes chained by event ID for sensitive events.
- Immutable object storage or WORM retention for production.
- Separate permission for reading audit logs and administering the system.
- Logs must redact secrets and personal identifiers where possible.

## 21. Monitoring

Dashboards:

- Portfolio equity, P/L, drawdown, exposure, concentration.
- Strategy performance and drift.
- Data feed freshness and vendor errors.
- Broker order state and reconciliation.
- Model error rates and hallucination tests.
- Risk block counts.
- Approval queue.
- System health.

Alerts:

- Kill switch activated.
- Risk limit breach.
- Data feed stale.
- Broker disconnected.
- Audit write failure.
- Unexpected order state.
- Position mismatch.
- Model output failed validation.
- Suspicious account activity.
- High latency during market hours.

## 22. General-Purpose AI Assistant Modules

Design all modules behind a permission system:

- Trading and portfolio module.
- Research module.
- Coding module.
- Document analysis module.
- Email/calendar automation module.
- Web browsing module.
- Financial reporting module.
- Business operations module.
- Long-term memory module.
- Multimodal input module.
- Tool-use and planning module.
- Autonomous workflow module.

Module isolation:

- Research module can read public data, not trade.
- Trading module can access order gateway only through policy checks.
- Email/calendar module cannot access broker tools.
- Coding module cannot read secrets by default.
- Memory module cannot store sensitive data without explicit approval.
- Admin module controls permissions but requires strong authentication and audit.

## 23. Implementation Roadmap

Phase 0: Project hardening

- Keep current `app.py` as prototype.
- Add README, architecture docs, requirements, environment template, and basic tests.
- Move config to `.env` and never commit secrets.
- Add structured logging.
- Add type hints and module boundaries.
- Expected output: clean repo, reproducible local setup, documented safety posture.
- Main risk: growing the script too fast without architecture.

Phase 1: Safe local research MVP

- Split code into modules: `atlas/research`, `atlas/market_data`, `atlas/llm`, `atlas/reports`, `atlas/risk`, `atlas/paper`.
- Replace plain JSON state with SQLite or PostgreSQL.
- Keep yfinance as non-production fallback, labeled clearly.
- Add SEC EDGAR connector for filings/company facts.
- Add FRED connector for macro data.
- Add report templates with citations and uncertainty labels.
- Add tests for risk checks and data parsing.
- Expected output: reliable research assistant, real-trading-ready data model, and paper portfolio tracker for rehearsal.
- Build first: configuration, logging, data models, risk policy object, and test harness.

Phase 2: Data foundation

- Add PostgreSQL, migrations, canonical schemas, and raw data storage.
- Add vendor abstraction for market data.
- Add data quality checks.
- Add pgvector and document embeddings.
- Add scheduled ingestion jobs.
- Expected output: persistent research database and source-grounded retrieval.
- Main risk: bad data silently entering the system.

Phase 3: Strategy lab

- Build event-driven backtester.
- Add point-in-time features.
- Add strategy definition format.
- Add metrics and backtest reports.
- Add overfitting controls and experiment tracking.
- Expected output: strategies can be tested, rejected, or promoted by evidence.
- Main risk: beautiful but biased backtests.

Phase 4: Paper trading production rehearsal

- Build internal paper broker and optional Alpaca paper adapter.
- Add order state machine.
- Add approval workflow even for paper mode.
- Add reconciliation, alerts, and risk blocks.
- Expected output: paper trading behaves like a safe rehearsal for real broker execution.
- Main risk: assuming paper results equal live results.

Phase 5: Portfolio and risk cockpit

- Add dashboard for exposure, drawdown, strategy performance, and alerts.
- Add sector, asset, liquidity, volatility, and event restrictions.
- Add manual kill switch.
- Add audit event viewer.
- Expected output: human operator can understand and control the system.
- Main risk: risk engine hidden behind opaque agent text.

Phase 6: Controlled real-money trading pilot

- Requires legal/compliance review, broker review, and production security review.
- Enable live equities only, no margin, no shorts, no options, no futures, no crypto.
- Use tiny capital.
- Require human approval for every order.
- Add daily sign-off and post-trade review.
- Expected output: real broker execution validated with minimal financial blast radius.
- Main risk: operational failure, not model failure.

Phase 7: Advanced institutional buildout

- Add streaming data with Kafka/Redpanda.
- Add ClickHouse/TimescaleDB for large-scale data.
- Add multi-strategy portfolio optimizer.
- Add factor risk model.
- Add compliance surveillance.
- Add tamper-evident/WORM audit storage.
- Add disaster recovery.
- Add formal model governance.
- Expected output: scalable multi-strategy research and execution platform.
- Main risk: complexity exceeding operational maturity.

Phase 8: General AI operating system

- Add coding, document, email/calendar, browser, reporting, and business modules.
- Add cross-module planner with permission-scoped tools.
- Add long-term memory governance.
- Add admin console for permissions and safety policies.
- Expected output: ATLAS becomes a general-purpose assistant where trading is one tightly controlled skill.
- Main risk: cross-module permission leakage.

## 24. What The Team Should Build First

Build in this order:

1. Safety and policy foundation: risk policy schema, permission model, action labels, audit log.
2. Repo hygiene: requirements, tests, README, module structure.
3. Data models: instruments, market data, filings, reports, broker accounts, positions, order intents, paper portfolio, risk events.
4. Source-grounded research: SEC EDGAR, FRED, market data abstraction, citations.
5. Deterministic risk engine: sizing, exposure, drawdown, liquidity, volatility, event restrictions.
6. Backtesting skeleton: event loop, portfolio accounting, costs, metrics.
7. Paper trading engine: order state machine, simulated fills, stops, reconciliation.
8. Dashboard: research reports, live/paper portfolio views, risk limits, approval queue, audit events.
9. Broker paper adapter: only after internal paper engine is stable.
10. Live broker adapter: only after explicit production approval, with real order submission gated behind risk checks and human approval.

Do not connect real broker execution first. The correct first engineering milestone is a safe research, risk, audit, and simulation foundation that can graduate into controlled real-money trading without rewriting the system.
