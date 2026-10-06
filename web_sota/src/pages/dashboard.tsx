import { Activity, Box, Cpu, Film, GitMerge, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ManagerStatus {
  status?: string;
  resolve_running?: boolean;
  api_available?: boolean;
}

interface ResolveInfo {
  status: string;
  version?: string;
  project_name?: string | null;
  is_rendering?: boolean;
  message?: string;
  manager_status?: ManagerStatus;
}

interface Onboarding {
  ready: boolean;
  recommended?: { provider: string; model: string | null };
  facts: string[];
}

export function Dashboard() {
  const [info, setInfo] = useState<ResolveInfo | null>(null);
  const [timeline, setTimeline] = useState<{
    name?: string;
    track_count_video?: number;
    track_count_audio?: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [hostState, setHostState] = useState<string>("unknown");
  const [hostPid, setHostPid] = useState<number | null>(null);
  const [onboarding, setOnboarding] = useState<Onboarding | null>(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await fetch("/api/v1/resolve-info");
        const data = await res.json();
        setInfo(data);
      } catch {
        setInfo({ status: "error", message: "Connection failed" });
      } finally {
        setLoading(false);
      }
    };
    const fetchHost = async () => {
      try {
        const r = await fetch("/api/v1/host-status");
        const d = await r.json();
        setHostState(d.state || "unknown");
        setHostPid(d.pid || null);
      } catch {
        /* ignore */
      }
    };
    const fetchTimeline = async () => {
      try {
        const r = await fetch("/api/v1/timeline");
        const d = await r.json();
        setTimeline(d.timeline);
      } catch {
        /* ignore */
      }
    };
    const fetchOnboarding = async () => {
      try {
        const r = await fetch("/api/v1/llm/onboarding");
        setOnboarding(await r.json());
      } catch {
        /* ignore */
      }
    };
    fetchInfo();
    fetchHost();
    fetchTimeline();
    fetchOnboarding();
    const interval = setInterval(fetchInfo, 5000);
    const hostInterval = setInterval(fetchHost, 10000);
    const tlInterval = setInterval(fetchTimeline, 10000);
    return () => {
      clearInterval(interval);
      clearInterval(hostInterval);
      clearInterval(tlInterval);
    };
  }, []);

  const isConnected = info?.status === "connected";
  const showOnboardingCue = !isConnected || onboarding?.ready === false;
  const disconnectHint = (() => {
    if (isConnected || !info) return null;
    if (info.status === "error") return "Backend API unreachable — restart the server or check port 10843.";
    const m = info.manager_status;
    if (m?.resolve_running === false || hostState === "not_installed")
      return "DaVinci Resolve is not installed or not running. Launch from the top bar.";
    if (hostState === "installed_stopped")
      return 'DaVinci Resolve is installed but not running. Click "Launch Resolve" in the top bar.';
    if (hostState === "ready" && m?.api_available === false)
      return `Resolve is running (PID ${hostPid}) but scripting API is inactive. Open a project in Resolve — the scripting bridge activates once a project is loaded.`;
    if (m?.api_available === false)
      return "Scripting API not available — enable external scripting in Resolve preferences, then open a project.";
    if (info.message) return info.message;
    return null;
  })();
  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Resolve Dashboard</h2>
          <p className="text-slate-300">Media production and project status</p>
        </div>
      </div>

      {showOnboardingCue ? (
        <div
          data-testid="onboarding-cue"
          className="rounded-lg border border-red-800 bg-red-950/40 p-4 text-sm text-red-200"
        >
          <p className="font-semibold">Get connected to start automating Resolve.</p>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-red-200/90">
            {!isConnected ? (
              <li>Start DaVinci Resolve, open a project, and enable external scripting — see Help.</li>
            ) : null}
            {onboarding?.ready === false ? (
              <li>No local LLM detected. Install Ollama and pull a model to enable Chat — see Settings.</li>
            ) : null}
          </ul>
        </div>
      ) : null}

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4" data-testid="kpi-grid">
        <Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-project">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Active Project</CardTitle>
            <Cpu className={isConnected ? "h-4 w-4 text-emerald-500" : "h-4 w-4 text-slate-600"} />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-slate-300 mt-2" />
            ) : (
              <>
                <div className="text-xl font-bold text-white truncate h-8 mt-1" title={info?.project_name || "None"}>
                  {isConnected ? info?.project_name || "None" : "Disconnected"}
                </div>
                <p className="text-sm text-slate-300 mt-1">Loaded in memory</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-render">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Render Engine</CardTitle>
            <Activity
              className={info?.is_rendering ? "h-4 w-4 text-orange-500 animate-pulse" : "h-4 w-4 text-blue-500"}
            />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-slate-300 mt-2" />
            ) : (
              <>
                <div className="text-2xl font-bold text-white">
                  {isConnected ? (info?.is_rendering ? "Rendering" : "Ready") : "Offline"}
                </div>
                <p className="text-sm text-slate-300">GPU Accelerated</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-version">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Resolve Version</CardTitle>
            <Box className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-slate-300 mt-2" />
            ) : (
              <>
                <div className="text-xl font-bold text-white truncate h-8 mt-1">
                  {isConnected ? info?.version : "Unknown"}
                </div>
                <p className="text-sm text-slate-300 mt-1">Detected from scripting bridge</p>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-connection">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">API Connection</CardTitle>
            <GitMerge className={isConnected ? "h-4 w-4 text-emerald-500" : "h-4 w-4 text-red-500"} />
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-slate-300 mt-2" />
            ) : (
              <>
                <div
                  className={isConnected ? "text-2xl font-bold text-emerald-400" : "text-2xl font-bold text-red-400"}
                >
                  {isConnected ? "Live" : "Disconnected"}
                </div>
                <p className="text-sm text-slate-300">Scripting bridge {isConnected ? "active" : "inactive"}</p>
                {!isConnected && disconnectHint ? (
                  <p className="text-sm text-amber-200/90 mt-2 leading-snug" title={disconnectHint}>
                    {disconnectHint}
                  </p>
                ) : null}
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 border-slate-800 bg-slate-950/50" data-testid="activity-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Activity className="h-4 w-4 text-emerald-400" />
              Production Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isConnected && timeline ? (
              <div className="space-y-4" data-testid="activity-live">
                <div className="flex items-center gap-4 p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                  <Film className="h-5 w-5 text-blue-400" />
                  <div>
                    <p className="text-sm font-medium text-white">{timeline.name || "Untitled"}</p>
                    <p className="text-sm text-slate-300">
                      {timeline.track_count_video ?? "?"} video tracks · {timeline.track_count_audio ?? "?"} audio
                      tracks
                    </p>
                  </div>
                </div>
                {info?.is_rendering && (
                  <div className="flex items-center gap-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <Loader2 className="h-5 w-5 text-amber-400 animate-spin" />
                    <div>
                      <p className="text-sm font-medium text-amber-300">Rendering in progress</p>
                      <p className="text-sm text-amber-400/70">Check render queue for details</p>
                    </div>
                  </div>
                )}
              </div>
            ) : isConnected ? (
              <div
                className="h-[100px] flex items-center justify-center border border-dashed border-slate-800 rounded-md"
                data-testid="activity-empty"
              >
                <p className="text-slate-300 text-sm">No timeline open</p>
              </div>
            ) : (
              <div
                className="h-[100px] flex items-center justify-center border border-dashed border-slate-800 rounded-md"
                data-testid="activity-empty"
              >
                <p className="text-slate-300 text-sm">Connect to Resolve to see activity</p>
              </div>
            )}
          </CardContent>
        </Card>
        <Card className="col-span-3 border-slate-800 bg-slate-950/50" data-testid="session-card">
          <CardHeader>
            <CardTitle className="text-white">Current Session</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <span className="relative flex h-2 w-2 mr-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <div className="ml-2 space-y-1">
                  <p className="text-sm font-medium leading-none text-white">
                    {isConnected ? (info?.project_name ?? "Connected") : "No session"}
                  </p>
                  <p className="text-sm text-slate-300">
                    {isConnected
                      ? `Resolve ${info?.version ?? ""} · scripting live`
                      : "Start Resolve and open a project"}
                  </p>
                </div>
                <div className="ml-auto font-mono text-sm text-slate-300" data-testid="host-state">
                  {hostState}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
