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

Run the foundation tests:

```powershell
python -m unittest discover -s tests
```

## Safety Position

ATLAS is intended for real trading, but live order submission must stay gated behind:

- Explicit production trading configuration.
- Human approval.
- Deterministic risk checks.
- Audit logging.
- Broker-state reconciliation.
- Shutdown controls.

The system must never expose broker credentials to prompts, reports, logs, or client-side code.

