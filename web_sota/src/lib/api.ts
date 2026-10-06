// API base: same-origin "/api/v1" in a browser tab (vite proxies /api to the
// backend on :10843). Absolute backend URL ONLY inside the Tauri WebView,
// where there is no dev-server proxy. (Fleet CORS rule: hardcoded absolute
// backend URLs outside a Tauri gate break every non-localhost tab.)
const IN_TAURI = typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;

export const API_BASE = IN_TAURI ? "http://127.0.0.1:10843/api/v1" : "/api/v1";
