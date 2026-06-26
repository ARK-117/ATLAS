# ATLAS

ATLAS is being built into a professional AI research and real-trading system. The current application is still early-stage, but the repo now has the first safety-critical trading foundation:

- Typed order intents.
- Deterministic pre-trade risk checks.
- Human approval objects.
- Append-only JSONL audit logging.
- Canonical append-only event spine for execution, risk, and governance events.
- Broker adapter boundary.
- Internal simulated broker for testing execution flow.
- Live broker execution intentionally unconfigured until credentials, reconciliation, production approval, and compliance controls are built.
- Web UI scaffold under `web-ui/`, with live trading locked by design.
- Native Tauri desktop shell under `desktop/`.
- Frontend-safe assistant runtime under `ai/runtime/`.

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
readiness
controls
kill switch on reason for stopping execution
kill switch clear CLEAR_KILL_SWITCH
policy profiles
policy show
policy use paper
intent buy NVDA 1 450 25 momentum thesis with stop defined
intents
intent show INTENT_ID
approve intent INTENT_ID APPROVE_LIVE_INTENT
recheck intent INTENT_ID
events
```

This creates and audits an order intent. It does not place a live broker order unless Live Production Mode, broker credentials, approval workflow, risk checks, and the execution adapter are configured.

Committed policy profiles live in `configs/risk_profiles/`. Runtime state such as the active local profile is stored in `atlas_data.json`, which is intentionally ignored by Git. Local production-style overrides should use `*.local.json`; those files are also ignored so live settings are not accidentally committed.

Canonical runtime events are written to `events/canonical_events.jsonl`, which is intentionally ignored by Git. Use the `events` command inside the app to inspect the latest local execution, risk, and governance events.

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
- `docs/FINAL_TARGET_ANALYSIS.md`

## Project Layout

```text
ai/        AI runtime and future AI service boundaries.
atlas/     Python trading, risk, governance, broker, and event foundations.
desktop/   Tauri native desktop shell and Windows launch helper.
web-ui/    React, TypeScript, Vite, and Tailwind frontend.
docs/      Architecture, safety, and implementation notes.
tests/     Python foundation tests.
```

## Web UI And Desktop Shell

The frontend is in `web-ui/`.

Use the immediate static preview without a dev server:

```text
web-ui/preview/index.html
```

After installing the frontend toolchain:

```powershell
cd web-ui
npm install
npm run dev
```

The desktop helper remains available:

```powershell
cd desktop
.\run-dev.cmd
```

For native Tauri packaging on Windows, Rust and Microsoft Visual C++ Build Tools with the C++ workload are required.
