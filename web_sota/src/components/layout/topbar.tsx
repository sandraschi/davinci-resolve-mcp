import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ExternalLink, HelpCircle, LayoutGrid, Loader2, Play, WifiOff } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { APPS_CATALOG } from "@/common/apps-catalog";

interface HostState {
  state: string;
  message: string;
  app_name: string;
  version?: string;
}

export function Topbar() {
  const [host, setHost] = useState<HostState | null>(null);
  const [launching, setLaunching] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch("/api/v1/host-status");
      const d = await r.json();
      setHost(d);
    } catch {
      setHost(null);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const t = setInterval(fetchStatus, 10000);
    return () => clearInterval(t);
  }, [fetchStatus]);

  const handleLaunch = async () => {
    setLaunching(true);
    try {
      await fetch("/api/v1/host/launch", { method: "POST" });
      setTimeout(fetchStatus, 5000);
    } finally {
      setLaunching(false);
    }
  };

  const state = host?.state || "unknown";
  const isReady = state === "ready";
  const canLaunch = state === "installed_stopped";

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-slate-400">
          Navigation / <span className="text-slate-100">Control Center</span>
        </h1>
      </div>

      <div className="flex items-center gap-2">
        {/* Resolve Status Indicator */}
        {isReady ? (
          <div className="mr-2 flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-500 border border-emerald-500/20">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            Resolve Live
          </div>
        ) : canLaunch ? (
          <div className="mr-2 flex items-center gap-2 rounded-full bg-amber-500/10 px-3 py-1 text-xs text-amber-400 border border-amber-500/20">
            <WifiOff className="h-3 w-3" />
            Resolve Stopped
            <button
              onClick={handleLaunch}
              disabled={launching}
              className="ml-1 inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 transition-colors disabled:opacity-50"
            >
              {launching ? <Loader2 className="h-2.5 w-2.5 animate-spin" /> : <Play className="h-2.5 w-2.5" />}
              Launch
            </button>
          </div>
        ) : (
          <div className="mr-2 flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400 border border-slate-700">
            <WifiOff className="h-3 w-3" />
            {state === "not_installed"
              ? "Not Installed"
              : state === "running_unreachable"
                ? "Connecting..."
                : "Offline"}
          </div>
        )}

        {/* Apps Navigation */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900/50 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-700">
              <LayoutGrid className="h-4 w-4" />
              Apps
            </button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[220px] animate-in fade-in zoom-in-95 data-[side=bottom]:slide-in-from-top-2 rounded-md border border-slate-800 bg-slate-950 p-1 shadow-xl"
              sideOffset={5}
              align="end"
            >
              <DropdownMenu.Label className="px-2 py-1.5 text-xs font-semibold text-slate-500">
                Switch Application
              </DropdownMenu.Label>

              <div className="h-px bg-slate-800 my-1" />

              {APPS_CATALOG.map((app) => (
                <DropdownMenu.Item key={app.id} asChild>
                  <a
                    href={app.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex w-full select-none items-center rounded-sm px-2 py-1.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white focus:bg-slate-800 focus:text-white outline-none cursor-pointer"
                  >
                    <app.icon className="mr-2 h-4 w-4 text-slate-400" />
                    <span>{app.label}</span>
                    <ExternalLink className="ml-auto h-3 w-3 opacity-50" />
                  </a>
                </DropdownMenu.Item>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <button className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
          <HelpCircle className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
