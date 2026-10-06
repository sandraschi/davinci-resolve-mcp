import { create } from "zustand";

const PROVIDER_KEY = "llm_provider";
const MODEL_KEY = "llm_model";

interface LlmState {
  providers: { id: string; label: string; detected: boolean; url: string }[];
  models: string[];
  provider: string;
  model: string;
  probing: boolean;
  gpuDetected: boolean;
  setProviders: (providers: LlmState["providers"]) => void;
  setModels: (models: string[]) => void;
  setProvider: (provider: string) => void;
  setModel: (model: string) => void;
  setProbing: (probing: boolean) => void;
  setGpuDetected: (gpuDetected: boolean) => void;
  refresh: () => Promise<void>;
}

function read(key: string, fallback: string): string {
  try {
    return localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

function write(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

export const useLlmStore = create<LlmState>((set, get) => ({
  providers: [],
  models: [],
  provider: read(PROVIDER_KEY, "ollama"),
  model: read(MODEL_KEY, ""),
  probing: true,
  gpuDetected: false,
  setProviders: (providers) => set({ providers }),
  setModels: (models) => set({ models }),
  setProvider: (provider) => {
    write(PROVIDER_KEY, provider);
    set({ provider, model: "" });
    write(MODEL_KEY, "");
  },
  setModel: (model) => {
    write(MODEL_KEY, model);
    set({ model });
  },
  setProbing: (probing) => set({ probing }),
  setGpuDetected: (gpuDetected) => set({ gpuDetected }),
  refresh: async () => {
    set({ probing: true });
    try {
      const d = await fetch("/api/v1/llm/discover").then((r) => (r.ok ? r.json() : { providers: [] }));
      const providers = d.providers || [];
      set({ providers });
      const detected = providers.some((p: { detected: boolean }) => p.detected);
      if (detected) {
        const m = await fetch("/api/v1/llm/models").then((r) => (r.ok ? r.json() : { models: [] }));
        const models: string[] = m.models || [];
        set({ models });
        const { model } = get();
        if (!model || !models.includes(model)) {
          const next = models[0] || "";
          write(MODEL_KEY, next);
          set({ model: next });
        }
      }
    } catch {
      /* backend unreachable: keep last known state */
    } finally {
      set({ probing: false });
    }
  },
}));
