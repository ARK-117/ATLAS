import type { AppContext, AssistantRuntimeResult } from "../types";

export interface AtlasStatus {
  mode: string;
  broker: string;
  market: string;
  dataFreshness: string;
  ai: string;
  risk: string;
  killSwitchActive: boolean;
  connected: boolean;
  tools?: {
    quote: boolean;
    webSearch: boolean;
    webpageFetch: boolean;
    liveTrading: boolean;
  };
}

const API_BASE_URL = import.meta.env.VITE_ATLAS_API_URL ?? "http://127.0.0.1:8000";

export async function fetchAtlasStatus(): Promise<AtlasStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/status`);
    if (!response.ok) {
      throw new Error(`status request failed: ${response.status}`);
    }
    return {
      ...((await response.json()) as Omit<AtlasStatus, "connected">),
      connected: true
    };
  } catch {
    return {
      mode: "Research Mode",
      broker: "Disconnected",
      market: "Monitoring",
      dataFreshness: "Backend offline",
      ai: "Backend offline",
      risk: "Normal",
      killSwitchActive: false,
      connected: false
    };
  }
}

export async function sendAssistantTurn(message: string, context: AppContext): Promise<AssistantRuntimeResult> {
  const response = await fetch(`${API_BASE_URL}/assistant/turn`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message, context })
  });

  if (!response.ok) {
    throw new Error(`assistant request failed: ${response.status}`);
  }

  return (await response.json()) as AssistantRuntimeResult;
}
