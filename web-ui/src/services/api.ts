export interface AtlasStatus {
  mode: string;
  broker: string;
  risk: string;
  killSwitchActive: boolean;
}

const API_BASE_URL = import.meta.env.VITE_ATLAS_API_URL ?? "http://127.0.0.1:8000";

export async function fetchAtlasStatus(): Promise<AtlasStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/status`);
    if (!response.ok) {
      throw new Error(`status request failed: ${response.status}`);
    }
    return (await response.json()) as AtlasStatus;
  } catch {
    return {
      mode: "Research Mode",
      broker: "Disconnected",
      risk: "Normal",
      killSwitchActive: false
    };
  }
}
