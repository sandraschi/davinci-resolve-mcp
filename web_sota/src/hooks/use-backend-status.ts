import { useEffect, useState } from "react";

export type BackendStatus = "online" | "offline" | "unknown";

/**
 * Backend status with Tauri event + HTTP poll fallback.
 *
 * Tries the Tauri `backend-status` event first (inside try/catch so the plain
 * browser build never crashes on the missing API), and always keeps an HTTP
 * poll against /api/v1/health with exponential-style backoff intervals.
 */
export function useBackendStatus(pollMs = 5000): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>("unknown");

  useEffect(() => {
    let cancelled = false;
    let unlisten: (() => void) | null = null;

    // 1. Tauri event path (guarded: plain browser has no __TAURI_INTERNALS__)
    try {
      const w = window as unknown as Record<string, unknown>;
      if ("__TAURI_INTERNALS__" in w) {
        import("@tauri-apps/api/event")
          .then(({ listen }) =>
            listen<string>("backend-status", (event) => {
              if (!cancelled && event.payload === "ready") setStatus("online");
            }),
          )
          .then((stop) => {
            unlisten = stop;
          })
          .catch(() => {
            /* fall through to HTTP poll */
          });
      }
    } catch {
      /* fall through to HTTP poll */
    }

    // 2. HTTP poll fallback (works everywhere the backend is reachable).
    // Failures back off exponentially (1s, 2s, 4s, 8s, 16s); success resets.
    let delay = 1000;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      if (cancelled) return;
      try {
        const r = await fetch("/api/v1/health");
        if (cancelled) return;
        setStatus(r.ok ? "online" : "offline");
        delay = r.ok ? pollMs : Math.min(delay * 2, 16000);
      } catch {
        if (cancelled) return;
        setStatus("offline");
        delay = Math.min(delay * 2, 16000);
      }
      if (!cancelled) timer = setTimeout(poll, delay);
    };
    poll();

    return () => {
      cancelled = true;
      clearTimeout(timer);
      if (unlisten) unlisten();
    };
  }, [pollMs]);

  return status;
}
