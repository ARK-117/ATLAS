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

The current runtime is frontend-safe and conservative. It can infer intent, build app context, create tool activity records, and block unavailable or unsafe actions. It does not claim to fetch real market data, web data, or broker state unless those tools are actually connected.

Future backend AI services should be added separately under a backend service package when the FastAPI layer is introduced.
