# ATLAS Desktop UI

This folder contains the first desktop UI layer for ATLAS.

## What Is Built

- Tauri desktop shell scaffold.
- React + TypeScript + Vite frontend scaffold.
- Tailwind CSS theme and ATLAS component styles.
- Dark command-center layout with:
  - Left navigation rail.
  - Top system status bar.
  - Main workspace.
  - Right AI intelligence panel.
  - Bottom event console.
- MVP pages:
  - Command Center.
  - Market Map.
  - Watchlist.
  - Asset Deep Dive.
  - Research Lab.
  - Portfolio.
  - Risk Center.
  - Paper Trading.
  - Live Trading locked screen.
  - Backtesting.
  - AI Agents.
  - Audit Logs.
  - Settings.

Live trading is intentionally locked in this UI. The frontend does not place broker orders and does not bypass the Python risk engine.

## Immediate Preview

This machine does not currently have Node/npm or Rust installed, so the Vite/Tauri app cannot be run here yet.

Open this file directly in a browser:

```text
desktop/preview/index.html
```

That preview is a zero-dependency version of the first command-center shell.

## Full Desktop Run

After installing Node.js LTS, Rust, and Tauri prerequisites:

```powershell
cd desktop
npm install
npm run dev
```

For the desktop shell:

```powershell
cd desktop
npm run tauri:dev
```

## Build Direction

Next steps:

1. Add a FastAPI backend surface for `/health`, `/status`, `/watchlist`, `/risk/status`, and `/audit/logs`.
2. Connect the UI API client to the existing Python core.
3. Replace preview values with backend-backed state.
4. Add WebSocket event streaming from the canonical event store.
5. Keep live trading locked until production readiness, broker integration, human approval, and audit controls are complete.
