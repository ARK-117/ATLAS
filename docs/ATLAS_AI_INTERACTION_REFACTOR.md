# ATLAS AI Interaction Refactor

This refactor moves ATLAS away from command-parser behavior and toward a natural desktop assistant embedded in the workstation UI.

## Current Implementation

- `desktop/src/ai/systemPrompt.ts` stores the in-app ATLAS behavior rules.
- `desktop/src/ai/contextBuilder.ts` builds app context for each assistant turn.
- `desktop/src/ai/intentRouter.ts` maps natural user wording to app intents.
- `desktop/src/ai/toolRegistry.ts` defines controlled tool activity records.
- `desktop/src/ai/assistantRuntime.ts` coordinates one assistant turn.
- `desktop/src/components/ai/` contains chat, input, tool activity, source, context, and confirmation UI.
- `desktop/src/components/command/CommandPalette.tsx` adds Ctrl+K command mode for navigation and freeform assistant requests.
- `desktop/src/layout/WorkspaceDimensions.tsx` exposes the blueprint dimensions: time, asset scope, intelligence lens, operating mode, confidence, and risk.

The runtime is intentionally conservative. If a real backend tool is not connected, ATLAS shows the planned blocked tool activity instead of inventing market data, web results, news, or broker actions.

## Safety Rules

- The UI does not submit live trades.
- Live trading remains locked unless production controls are configured.
- Web research must use backend tools before ATLAS can claim it searched or fetched sources.
- Market facts require configured market-data tools.
- Sensitive actions need confirmation cards.

## Next Backend Step

Create FastAPI modules under:

```text
backend/app/ai/
  assistant_runtime.py
  system_prompt.py
  intent_router.py
  context_builder.py
  memory.py
  tool_registry.py
  response_formatter.py
  safety.py
```

The frontend runtime can then become a UI client for the backend assistant runtime.
