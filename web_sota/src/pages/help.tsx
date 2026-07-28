import { Film, Globe, HelpCircle, List, Music2, Server } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_BASE = "/api/v1";

export function Help() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <HelpCircle className="h-7 w-7 text-blue-500" />
          Help & Documentation
        </h2>
        <p className="text-slate-400 mt-1">Webapp, MCP server, DaVinci Resolve, and Fairlight</p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Globe className="h-5 w-5 text-blue-400" />
            Webapp
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-300 text-sm">
          <p>
            The Resolve-MCP webapp is a local dashboard that talks to the same backend as the MCP server. All API calls
            use the same base: <code className="bg-slate-800 px-1 rounded">{API_BASE}</code>.
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <strong>Overview</strong> – Dashboard and connection status.
            </li>
            <li>
              <strong>Projects</strong> – Browse and open Resolve projects.
            </li>
            <li>
              <strong>Timeline</strong> – Current timeline info and clip list.
            </li>
            <li>
              <strong>Fairlight</strong> – Audio tracks: list, mute, solo, volume; open Fairlight page in Resolve.
            </li>
            <li>
              <strong>Render Queue</strong> – Render jobs and presets.
            </li>
            <li>
              <strong>Video Tools</strong> – Media pool, LUTs, timelines.
            </li>
            <li>
              <strong>Production Actions</strong> – High-level actions (import, apply LUT, render).
            </li>
            <li>
              <strong>AI Editor (Chat)</strong> – Chat with a local LLM; pick and load a model in Settings first.
            </li>
            <li>
              <strong>System Logs</strong> – Live server log buffer (refresh or auto-refresh).
            </li>
            <li>
              <strong>Settings</strong> – Resolve API bridge (host/port), default FPS/resolution, and{" "}
              <strong>Local LLM</strong> (Ollama URL, list models, load model).
            </li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Server className="h-5 w-5 text-blue-400" />
            MCP Server
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-300 text-sm">
          <p>
            The DaVinci Resolve MCP server exposes tools to AI assistants (Claude, Cursor, etc.) via the Model Context
            Protocol. Connect it in your IDE or Claude Desktop config; it runs over stdio or SSE.
          </p>
          <p>
            <strong>Portmanteau tools</strong> – One tool per domain with an{" "}
            <code className="bg-slate-800 px-1 rounded">operation</code> argument:
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <code>resolve_fairlight(operation=open_page|get_tracks|set_mute|set_solo|set_volume, ...)</code> –
              Fairlight page and timeline audio.
            </li>
            <li>Other portmanteau tools for media pool, timelines, LUTs, render, etc.</li>
          </ul>
          <p>
            The server must run with access to the Resolve Scripting API (same machine as Resolve, or a bridge). Webapp
            and MCP share the same backend process when you start the server with the web UI.
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Film className="h-5 w-5 text-blue-400" />
            DaVinci Resolve
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-300 text-sm">
          <p>
            Control is via the <strong>Resolve Scripting API</strong> (Lua or Python). This MCP uses a small bridge that
            runs inside Resolve or as a helper process.
          </p>
          <p>
            <strong>Typical workflows</strong>:
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>Open project → get current timeline → list clips / add to timeline.</li>
            <li>Apply LUTs or color corrections to clips.</li>
            <li>Create render jobs with a given preset and output path.</li>
            <li>Fairlight: open page, get tracks, set mute/solo/volume.</li>
          </ul>
          <p>
            Ensure Resolve is running and the API bridge (host/port in Settings) is reachable. The Overview page shows
            connection status.
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Music2 className="h-5 w-5 text-blue-400" />
            Fairlight
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-300 text-sm">
          <p>Fairlight is the DAW inside DaVinci Resolve. From the webapp or MCP you can:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <strong>Open Fairlight page</strong> – Switch Resolve UI to the Fairlight tab.
            </li>
            <li>
              <strong>Get tracks</strong> – List audio tracks for the current (or named) timeline.
            </li>
            <li>
              <strong>Set mute</strong> – Mute or unmute a track by 1-based index.
            </li>
            <li>
              <strong>Set solo</strong> – Solo or unsolo a track by 1-based index.
            </li>
            <li>
              <strong>Set volume</strong> – Set track volume (0.0–2.0) by 1-based index.
            </li>
          </ul>
          <p>
            MCP: use the portmanteau tool <code className="bg-slate-800 px-1 rounded">resolve_fairlight</code> with{" "}
            <code className="bg-slate-800 px-1 rounded">operation</code> one of:{" "}
            <code className="bg-slate-800 px-1 rounded">open_page</code>,{" "}
            <code className="bg-slate-800 px-1 rounded">get_tracks</code>,{" "}
            <code className="bg-slate-800 px-1 rounded">set_mute</code>,{" "}
            <code className="bg-slate-800 px-1 rounded">set_solo</code>,{" "}
            <code className="bg-slate-800 px-1 rounded">set_volume</code>. Webapp: use the Fairlight page for tracks and
            the &quot;Open Fairlight page in Resolve&quot; button.
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <List className="h-5 w-5 text-blue-400" />
            System Logs
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-slate-300 text-sm">
          <p>
            The <strong>System Logs</strong> page shows the server&apos;s in-memory log buffer: timestamp, level, logger
            name, message, and optional exception. Use Refresh or enable Auto-refresh. Useful for debugging API and MCP
            tool calls.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
