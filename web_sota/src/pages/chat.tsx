import { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, Send, User, Loader2 } from "lucide-react";

const API_BASE = "/api/v1";
const CHAT_MODEL_KEY = "resolve-mcp-chat-model";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
}

interface ModelsResponse {
    models: string[];
    error?: string;
}

export function Chat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [models, setModels] = useState<string[]>([]);
    const [selectedModel, setSelectedModel] = useState<string>("");
    const [loading, setLoading] = useState(false);
    const [loadingModels, setLoadingModels] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const bottomRef = useRef<HTMLDivElement>(null);

    const loadModels = async () => {
        setLoadingModels(true);
        setError(null);
        const maxAttempts = 3;
        const delayMs = 2000;
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const res = await fetch(`${API_BASE}/llm/models`);
                const data: ModelsResponse = await res.json();
                setModels(data.models || []);
                setError(data.error || null);
                const saved = localStorage.getItem(CHAT_MODEL_KEY);
                if (data.models?.length) {
                    if (saved && data.models.includes(saved)) {
                        setSelectedModel(saved);
                    } else {
                        setSelectedModel(data.models[0]);
                        localStorage.setItem(CHAT_MODEL_KEY, data.models[0]);
                    }
                }
                break;
            } catch (e) {
                const msg = e instanceof Error ? e.message : "Failed to load models";
                setError(attempt < maxAttempts ? `Backend starting... (${attempt}/${maxAttempts})` : msg);
                setModels([]);
                if (attempt < maxAttempts) {
                    await new Promise((r) => setTimeout(r, delayMs));
                }
            }
        }
        setLoadingModels(false);
    };

    useEffect(() => {
        loadModels();
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const onSelectModel = (name: string) => {
        setSelectedModel(name);
        localStorage.setItem(CHAT_MODEL_KEY, name);
    };

    const sendMessage = async () => {
        const text = input.trim();
        if (!text || !selectedModel || loading) return;

        setInput("");
        const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
        setMessages((prev) => [...prev, userMsg]);
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE}/llm/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ model: selectedModel, prompt: text }),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || res.statusText);
            }
            const data = await res.json();
            const assistantMsg: Message = {
                id: crypto.randomUUID(),
                role: "assistant",
                content: data.response || "",
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Generate failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">AI Video Editor</h2>
                    <p className="text-slate-400">Chat with a local LLM (Ollama). Pick a model in Settings or below.</p>
                </div>
                <div className="flex items-center gap-2">
                    <label className="text-slate-400 text-sm">Model:</label>
                    <select
                        className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 text-sm min-w-[160px]"
                        value={selectedModel}
                        onChange={(e) => onSelectModel(e.target.value)}
                        disabled={loadingModels || models.length === 0}
                    >
                        {loadingModels && <option>Loading...</option>}
                        {!loadingModels && models.length === 0 && <option>No models (start Ollama)</option>}
                        {models.map((m) => (
                            <option key={m} value={m}>{m}</option>
                        ))}
                    </select>
                </div>
            </div>

            {error && (
                <div className="mb-2 text-sm text-amber-400 bg-amber-500/10 border border-amber-500/30 rounded px-3 py-2">
                    {error}
                </div>
            )}

            <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col mb-4 overflow-hidden">
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.length === 0 && (
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/30 shrink-0">
                                <Bot className="w-5 h-5 text-blue-400" />
                            </div>
                            <div className="flex-1 text-slate-400 text-sm">
                                {selectedModel
                                    ? "Send a message to start. Example: \"Suggest a cut at 00:01:30\" or \"How do I apply a LUT?\""
                                    : "Select a model (or add one in Settings / Ollama) to chat."}
                            </div>
                        </div>
                    )}
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
                        >
                            <div
                                className={`w-8 h-8 rounded-full flex items-center justify-center border shrink-0 ${
                                    msg.role === "assistant"
                                        ? "bg-blue-600/20 border-blue-500/30"
                                        : "bg-slate-800 border-slate-700"
                                }`}
                            >
                                {msg.role === "assistant" ? (
                                    <Bot className="w-5 h-5 text-blue-400" />
                                ) : (
                                    <User className="w-5 h-5 text-slate-300" />
                                )}
                            </div>
                            <div
                                className={`flex-1 max-w-[85%] text-sm p-3 rounded-md ${
                                    msg.role === "assistant"
                                        ? "bg-slate-900/50 border border-slate-800 text-slate-300"
                                        : "bg-blue-600/10 border border-blue-600/20 text-slate-300"
                                }`}
                            >
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/30 shrink-0">
                                <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                            </div>
                            <div className="text-slate-500 text-sm">Thinking...</div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </CardContent>

                <div className="p-4 border-t border-slate-800 bg-slate-900/20">
                    <div className="flex gap-2">
                        <Input
                            className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-500"
                            placeholder="Ask the AI (e.g., suggest an edit or explain a step)"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                            disabled={!selectedModel || loading}
                        />
                        <Button
                            className="bg-blue-600 hover:bg-blue-700"
                            onClick={sendMessage}
                            disabled={!input.trim() || !selectedModel || loading}
                        >
                            <Send className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
