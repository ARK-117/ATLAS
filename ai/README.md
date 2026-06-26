# ATLAS AI

This folder contains AI-facing code that should not live inside the web UI.

Current structure:

```text
ai/
  runtime/
    assistantRuntime.ts
    contextBuilder.ts
    intentRouter.ts
    systemPrompt.ts
    toolRegistry.ts
    types.ts
```

The current runtime is frontend-safe and conservative. It can infer intent, build app context, create tool activity records, and block unavailable or unsafe actions. The web UI calls `backend/server.py` first; this runtime remains the offline fallback.

Future backend AI services should be added separately under a backend service package when the FastAPI layer is introduced.
