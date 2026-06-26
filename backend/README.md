# ATLAS Backend

This folder contains the local HTTP API that connects the web UI to ATLAS tools.

The first backend is intentionally lightweight and uses Python's standard library so ATLAS can run without installing FastAPI yet. It exposes safe local endpoints for:

- System status.
- Watchlist state.
- Delayed market quotes through `yfinance` when installed.
- Public web search through `ddgs` when installed.
- Webpage extraction through `trafilatura` when installed.
- Assistant turns that use real backend tool activity instead of fake UI-only responses.

Live trading stays locked. This backend does not submit broker orders.

## Run

```powershell
cd D:\AI\TAI\atlas-ai
.\backend\run-backend.cmd
```

The desktop helper also starts this backend automatically when possible:

```powershell
cd D:\AI\TAI\atlas-ai\desktop
.\run-dev.cmd
```

## Endpoints

```text
GET  /health
GET  /status
GET  /watchlist
GET  /market/quote/{symbol}
GET  /market/news/{symbol}
GET  /web/search?q=...
GET  /web/page?url=...
POST /assistant/turn
```
