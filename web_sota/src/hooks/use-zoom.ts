import { useEffect } from "react";

const ZOOM_KEY = "resolve-mcp-ui-zoom";
const MIN_ZOOM = 0.8;
const MAX_ZOOM = 1.5;
const STEP = 0.1;

function readZoom(): number {
  try {
    const raw = Number(localStorage.getItem(ZOOM_KEY));
    if (Number.isFinite(raw)) return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, raw));
  } catch {
    /* ignore */
  }
  return 1;
}

/**
 * Ctrl+Scroll UI zoom (fleet webapp standard).
 *
 * Ctrl+wheel adjusts a zoom factor persisted in localStorage; Ctrl+0 resets.
 * Applied via the CSS `zoom` property on the document element (Chromium).
 */
export function useZoom(): void {
  useEffect(() => {
    const apply = (value: number) => {
      const clamped = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Math.round(value * 100) / 100));
      document.documentElement.style.setProperty("zoom", String(clamped));
      try {
        localStorage.setItem(ZOOM_KEY, String(clamped));
      } catch {
        /* ignore */
      }
    };

    apply(readZoom());

    const onWheel = (e: WheelEvent) => {
      if (!e.ctrlKey) return;
      e.preventDefault();
      apply(readZoom() + (e.deltaY < 0 ? STEP : -STEP));
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "0") {
        e.preventDefault();
        apply(1);
      }
    };
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("keydown", onKey);
    };
  }, []);
}
