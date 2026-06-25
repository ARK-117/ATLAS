# ATLAS

ATLAS is being built into a professional AI research and real-trading system. The current application is still early-stage, but the repo now has the first safety-critical trading foundation:

- Typed order intents.
- Deterministic pre-trade risk checks.
- Human approval objects.
- Append-only JSONL audit logging.
- Broker adapter boundary.
- Internal simulated broker for testing execution flow.
- Live broker execution intentionally unconfigured until credentials, reconciliation, production approval, and compliance controls are built.

## Current Commands

Run the original prototype:

```powershell
python app.py
```

Install prototype dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the foundation tests:

```powershell
python -m unittest discover -s tests
```

Create a real-trading order intent risk check:

```powershell
python app.py
```

Then in the ATLAS prompt:

```text
live policy
intent buy NVDA 1 450 25 momentum thesis with stop defined
```

This creates and audits an order intent. It does not place a live broker order unless Live Production Mode, broker credentials, approval workflow, risk checks, and the execution adapter are configured.

## Safety Position

ATLAS is intended for real trading, but live order submission must stay gated behind:

- Explicit production trading configuration.
- Live Production Mode.
- Permission levels from `docs/LIVE_TRADING_POLICY.md`.
- Human approval.
- Deterministic risk checks.
- Audit logging.
- Broker-state reconciliation.
- Shutdown controls.

The system must never expose broker credentials to prompts, reports, logs, or client-side code.

Read the live trading policy before implementing broker execution:

- `docs/LIVE_TRADING_POLICY.md`
