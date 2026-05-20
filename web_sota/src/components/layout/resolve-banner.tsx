import { useState, useEffect, useCallback } from "react";
import { cn } from "@/common/utils";
import { AlertCircle, Loader2, Play, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface HostStatus {
  success: boolean;
  state: string;
  app_name: string;
  message: string;
  version?: string;
  install_path?: string;
  pid?: number;
  download_url?: string;
  launch_cmd?: string;
}

interface Props {
  className?: string;
}

const stateColors: Record<string, string> = {
  ready: "border-emerald-500/20 bg-emerald-500/5 text-emerald-400",
  running_unreachable: "border-amber-500/20 bg-amber-500/5 text-amber-400",
  installed_stopped: "border-slate-700 bg-slate-900/50 text-slate-400",
  not_installed: "border-red-500/20 bg-red-500/5 text-red-400",
};

export function ResolveBanner({ className }: Props) {
  const [status, setStatus] = useState<HostStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [launchMsg, setLaunchMsg] = useState("");

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch("/api/v1/host-status");
      const d = await r.json();
      setStatus(d);
      setLoading(false);
    } catch {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 8000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const handleLaunch = async () => {
    setLaunching(true);
    setLaunchMsg("");
    try {
      const r = await fetch("/api/v1/host/launch", { method: "POST" });
      const d = await r.json();
      setLaunchMsg(d.message || "Launching...");
      setTimeout(fetchStatus, 4000);
    } catch {
      setLaunchMsg("Launch request failed");
    } finally {
      setLaunching(false);
    }
  };

  if (loading) return null;

  const state = status?.state || "unknown";
  const isReady = state === "ready";

  if (isReady) return null;

  const colorClass = stateColors[state] || stateColors.not_installed;
  const canLaunch = state === "installed_stopped";
  const isNotInstalled = state === "not_installed";

  return (
    <div className={cn("rounded-lg border p-4", colorClass, className)}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          {isReady ? (
            <Wifi className="h-5 w-5 mt-0.5 shrink-0" />
          ) : (
            <WifiOff className="h-5 w-5 mt-0.5 shrink-0" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {status?.app_name || "DaVinci Resolve"}
              </span>
              <Badge className={cn("text-[10px] border", colorClass)}>
                {status?.state?.replace(/_/g, " ").toUpperCase()}
              </Badge>
            </div>
            <p className="text-xs mt-1 opacity-80">
              {launchMsg || status?.message || "Connection unavailable"}
            </p>
            {status?.install_path && (
              <p className="text-[10px] mt-1 opacity-50">
                Install path: {status.install_path}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {canLaunch && (
            <button
              onClick={handleLaunch}
              disabled={launching}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 transition-colors text-xs font-medium disabled:opacity-50"
            >
              {launching ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Play className="h-3.5 w-3.5" />
              )}
              Launch Resolve
            </button>
          )}
          {isNotInstalled && status?.download_url && (
            <a
              href={status.download_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400 hover:bg-blue-500/20 transition-colors text-xs font-medium"
            >
              Download Resolve
            </a>
          )}
          <button
            onClick={fetchStatus}
            className="p-1.5 rounded hover:bg-slate-800/50 transition-colors"
            title="Refresh status"
          >
            <Loader2 className={cn("h-3.5 w-3.5 opacity-50", loading && "animate-spin")} />
          </button>
        </div>
      </div>
    </div>
  );
}
