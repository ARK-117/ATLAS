# ATLAS Final Target Analysis

The latest target specification describes ATLAS as a two-plane system:

- Research plane: ingest, normalize, analyze, model, explain, and store market/fundamental/news/alternative data.
- Execution plane: isolate broker connectivity behind policy, risk, approvals, kill switches, audit logs, and reconciliation.

The current implementation is still a local prototype, but it now has the right control spine for a live-capable system:

- Permissioned live-trading policy levels.
- Persistent risk profiles.
- Real-trading order intents.
- Human approval records.
- Append-only JSONL audit events.
- Global kill switch.
- Domain-based production readiness checks.
- Live broker execution blocked by default.

## Implemented Control Domains

| Target domain | Current implementation |
| --- | --- |
| Execution isolation | `LiveBrokerNotConfiguredAdapter`, policy profile gates, Live Production Mode flags |
| Human control | `APPROVE_LIVE_INTENT` approval workflow with expiry |
| Kill switches | persistent global kill switch with audit events |
| Order sanity | duplicate-check policy flag, required order intent fields, notional and size checks |
| Exposure | single-name, sector, gross exposure, cash, and drawdown checks |
| Liquidity | ADV, spread, market-data age, and volatility checks |
| Lineage | order intent, approval, risk check, broker result, and kill-switch audit events |
| Governance | domain-based readiness evaluator in `atlas/trading/governance.py` |

## Important Gaps

These are intentionally not complete yet:

- Canonical market/fundamental/news event schemas.
- Durable database layer.
- Portfolio/account reconciliation.
- Model registry and model-validation records.
- Backtesting and simulation engine.
- Real broker adapter.
- FIX/OMS/EMS connectivity.
- Market data recovery/replay.
- Monitoring dashboards.
- Incident playbooks and runbooks.

## Build Priority

The next implementation priority should be the canonical event and research data layer. That lets ATLAS start storing source-grounded market, filing, news, signal, order, fill, risk, and audit events in a consistent shape before adding databases, backtesting, or broker adapters.

