import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RefreshCw, Loader2 } from "lucide-react";

const API_BASE = "/api/v1";

interface ModelsResponse {
    models: string[];
    ollama_url?: string;
    error?: string;
}

export function Settings() {
    const [models, setModels] = useState<string[]>([]);
    const [ollamaUrl, setOllamaUrl] = useState<string>("");
    const [loadingModels, setLoadingModels] = useState(false);
    const [loadingModel, setLoadingModel] = useState<string | null>(null);
    const [llmError, setLlmError] = useState<string | null>(null);

    const fetchModels = async () => {
        setLoadingModels(true);
        setLlmError(null);
        const maxAttempts = 3;
        const delayMs = 2000;
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const res = await fetch(`${API_BASE}/llm/models`);
                const data: ModelsResponse = await res.json();
                setModels(data.models || []);
                if (data.ollama_url) setOllamaUrl(data.ollama_url);
                if (data.error) setLlmError(data.error);
                break;
            } catch (e) {
                setLlmError(attempt < maxAttempts ? "Backend starting... retrying." : (e instanceof Error ? e.message : "Failed to fetch models"));
                setModels([]);
                if (attempt < maxAttempts) await new Promise((r) => setTimeout(r, delayMs));
            }
        }
        setLoadingModels(false);
    };

    useEffect(() => {
        fetchModels();
    }, []);

    const loadModel = async (name: string) => {
        setLoadingModel(name);
        setLlmError(null);
        try {
            const res = await fetch(`${API_BASE}/llm/load?name=${encodeURIComponent(name)}`, { method: "POST" });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || res.statusText);
            }
        } catch (e) {
            setLlmError(e instanceof Error ? e.message : "Load failed");
        } finally {
            setLoadingModel(null);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
                <p className="text-slate-400">Manage connections and preferences</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">DaVinci Resolve API Bridge</CardTitle>
                        <CardDescription className="text-slate-400">Connection details for the Resolve Scripting API</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Bridge Host</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="localhost"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">Bridge Port</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="8080"
                                type="number"
                            />
                        </div>
                        <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
                            Test API Connection
                        </Button>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Local LLM (Ollama)</CardTitle>
                        <CardDescription className="text-slate-400">
                            Find and load models for the AI Editor chat. Server uses OLLAMA_URL (e.g. http://127.0.0.1:11434).
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {ollamaUrl && (
                            <p className="text-slate-500 text-sm">Backend Ollama: {ollamaUrl}</p>
                        )}
                        {llmError && (
                            <p className="text-amber-400 text-sm">{llmError}</p>
                        )}
                        <Button
                            variant="outline"
                            className="border-slate-800 text-slate-300 hover:bg-slate-800"
                            onClick={fetchModels}
                            disabled={loadingModels}
                        >
                            {loadingModels ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                            <span className="ml-2">Refresh model list</span>
                        </Button>
                        {models.length > 0 ? (
                            <ul className="space-y-2">
                                {models.map((name) => (
                                    <li key={name} className="flex items-center justify-between gap-2 py-1 border-b border-slate-800 last:border-0">
                                        <span className="text-slate-300 text-sm truncate">{name}</span>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="border-slate-700 text-slate-300 shrink-0"
                                            onClick={() => loadModel(name)}
                                            disabled={loadingModel !== null}
                                        >
                                            {loadingModel === name ? <Loader2 className="w-4 h-4 animate-spin" /> : "Load into memory"}
                                        </Button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            !loadingModels && <p className="text-slate-500 text-sm">No models found. Install Ollama and pull a model (e.g. ollama pull llama3.2).</p>
                        )}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Professional Preferences</CardTitle>
                        <CardDescription className="text-slate-400">Default project and timeline settings</CardDescription>
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
