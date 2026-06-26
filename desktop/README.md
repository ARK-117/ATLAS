# ATLAS Desktop Shell

This folder is now the native desktop wrapper for ATLAS.

It contains:

- `src-tauri/` for the Tauri desktop application.
- `run-dev.cmd` for the familiar Windows launch command.
- A small `package.json` that delegates frontend commands to `../web-ui`.

The React/Vite frontend source now lives in:

```text
../web-ui
```

The TypeScript assistant runtime now lives in:

```text
../ai/runtime
```

## Run From This Folder

```powershell
cd desktop
.\run-dev.cmd
```

PowerShell still requires the `.\` prefix for scripts in the current folder.

This starts the local backend on `http://127.0.0.1:8000` if it is not already running, then starts the web UI on `http://127.0.0.1:5173`.

## Native Tauri

The web UI builds successfully through `web-ui`. Native Tauri packaging on Windows still requires Rust and Microsoft Visual C++ Build Tools with the C++ workload. If the build fails with `link.exe not found`, install or repair Visual Studio Build Tools and include `Microsoft.VisualStudio.Workload.VCTools`.
