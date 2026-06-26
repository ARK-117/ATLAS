# ATLAS Web UI

This folder contains the React + TypeScript + Vite frontend for ATLAS.

It owns:

- App shell and routing.
- Pages and reusable UI components.
- Tailwind theme and global styles.
- Mock UI data used before the backend is connected.
- Browser-facing services such as `src/services/api.ts`.

It does not own the assistant runtime. The UI imports that from:

```text
../ai/runtime
```

## Run

Start the local backend first:

```powershell
cd ..
.\backend\run-backend.cmd
```

Then start the web UI:

```powershell
cd web-ui
npm install
npm run dev
```

The desktop helper starts both when possible:

```powershell
cd desktop
.\run-dev.cmd
```

## Build

```powershell
cd web-ui
npm run build
```

Live trading remains locked in the UI. The frontend must not bypass backend risk checks, approval gates, audit logging, or broker execution boundaries.
