// API base: production (installed Tauri app) uses the baked operator URL;
// dev browser uses same-origin /api/v1 (vite proxies to the dev backend);
// Tauri dev WebView uses the dev backend directly (no proxy there).
// (Fleet Tauri rule: hardcoded absolute backend URLs outside a Tauri gate
// break every non-localhost tab; relative /api breaks the installed app,
// which has no dev-server proxy. This covers all three.)
const BAKED: string = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "";
const IN_TAURI = typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;

function computeBase(): string {
  // API_BASE always ends with /api/v1 in every environment.
  if (!import.meta.env.DEV) return BAKED || "http://127.0.0.1:11238/api/v1";
  if (IN_TAURI) return "http://127.0.0.1:10843/api/v1";
  return "/api/v1";
}

export const API_BASE = computeBase();

/** Absolute-or-relative API URL for direct fetch() call sites. */
export function apiUrl(path: string): string {
  return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}
