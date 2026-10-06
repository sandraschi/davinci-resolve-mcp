import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLlmStore } from "@/store/llm";

function detectGpu(): string | null {
  try {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl");
    if (!gl) return null;
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    const renderer = ext ? String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : String(gl.getParameter(gl.RENDERER));
    return /nvidia|geforce|rtx|radeon|amd|apple|intel/i.test(renderer) ? renderer : null;
  } catch {
    return null;
  }
}

function LLMSettings() {
  const {
    providers,
    models,
    provider: selectedProvider,
    model: selectedModel,
    setProvider,
    setModel,
    refresh,
    probing,
    setGpuDetected,
  } = useLlmStore();
  const [gpu, setGpu] = useState<string | null>(null);
  useEffect(() => {
    refresh();
    const found = detectGpu();
    setGpu(found);
    setGpuDetected(found !== null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const detected = providers.some((p) => p.detected);
  return (
    <div className="space-y-3" data-testid="settings-llm-controls">
      {gpu && !detected && !probing ? (
        <p
          className="rounded-md border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-300"
          data-testid="llm-gpu-hint"
        >
          GPU detected ({gpu}) but no local LLM is running — install Ollama and pull a model to enable Chat.
        </p>
      ) : null}
      <select
        data-testid="llm-provider-select"
        className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
        value={selectedProvider}
        onChange={(e) => setProvider(e.target.value)}
      >
        <option value="ollama">Ollama</option>
        <option value="lmstudio">LM Studio</option>
      </select>
      <select
        data-testid="llm-model-select"
        className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
        value={selectedModel}
        onChange={(e) => setModel(e.target.value)}
      >
        {probing && <option>Probing providers...</option>}
        {!probing && models.length === 0 && <option value="">No models detected</option>}
        {models.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>
    </div>
  );
}

export function Settings() {
  return (
    <div className="space-y-6" data-testid="settings-page">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
        <p className="text-slate-300">Manage connections and preferences</p>
      </div>

      <div className="grid gap-6">
        <Card className="border-slate-800 bg-slate-950/50" data-testid="settings-bridge">
          <CardHeader>
            <CardTitle className="text-white">DaVinci Resolve API Bridge</CardTitle>
            <CardDescription className="text-slate-300">
              Connection details for the Resolve Scripting API
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">Bridge Host</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                defaultValue="127.0.0.1"
              />
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Bridge Port</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                defaultValue="10843"
                type="number"
              />
            </div>
            <Button
              variant="outline"
              className="border-slate-800 text-slate-300 hover:bg-slate-800"
              data-testid="settings-test-connection"
            >
              Test API Connection
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="settings-llm">
          <CardHeader>
            <CardTitle className="text-white">Local LLM</CardTitle>
            <CardDescription className="text-slate-300">Provider and model selection</CardDescription>
          </CardHeader>
          <CardContent>
            <LLMSettings />
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="settings-preferences">
          <CardHeader>
            <CardTitle className="text-white">Professional Preferences</CardTitle>
            <CardDescription className="text-slate-300">Default project and timeline settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label className="text-slate-300">Default Timeline FPS</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                defaultValue="23.976"
              />
            </div>
            <div className="grid gap-2">
              <Label className="text-slate-300">Standard Resolution</Label>
              <Input
                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                defaultValue="3840x2160 (4K UHD)"
              />
            </div>
            <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
              Save Preferences
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
