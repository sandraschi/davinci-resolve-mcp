import { Bot, Download, Loader2, Send, Trash2, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const API_BASE = "/api/v1";
const CHAT_MODEL_KEY = "resolve-mcp-chat-model";
const CHAT_PERSONALITY_KEY = "resolve-mcp-chat-personality";
const CHAT_HISTORY_KEY = "resolve-mcp-chat-history";
const HISTORY_CAP = 100;

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ModelsResponse {
  models: string[];
  error?: string;
}

interface Skill {
  name: string;
  uri: string;
  description: string;
  operations: string[];
}

const PERSONALITIES: Record<string, string> = {
  Editor: "You are a senior video editor. Answer with concrete Resolve steps and tool actions.",
  Colorist: "You are a color scientist. Answer with node trees, scopes guidance, and exact parameter values.",
  "Fairlight Engineer":
    "You are a Fairlight mixing engineer. Answer with track routing, EQ/dynamics settings, and loudness targets.",
  "Render Wrangler": "You are a finishing artist. Answer with delivery presets, codecs, and render-queue checks.",
  Custom: "",
};

const EXAMPLE_PROMPTS = [
  "Suggest a cut at 00:01:30 for a talking-head interview",
  "How do I apply a LUT to every clip on the timeline?",
  "EQ my dialogue track for clarity",
  "Which render preset should I use for YouTube 4K?",
  "List my Resolve projects",
  "How do I export subtitles as SRT?",
];

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(CHAT_HISTORY_KEY);
    const parsed = raw ? (JSON.parse(raw) as Message[]) : [];
    return Array.isArray(parsed) ? parsed.slice(-HISTORY_CAP) : [];
  } catch {
    return [];
  }
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>(loadHistory);
  const [input, setInput] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [personality, setPersonality] = useState<string>(() => localStorage.getItem(CHAT_PERSONALITY_KEY) || "Editor");
  const [customPersonality, setCustomPersonality] = useState("");
  const [skills, setSkills] = useState<Skill[]>([]);
  const [providerOk, setProviderOk] = useState<boolean | null>(null);
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

  // Skill-first: load skill registry + provider status on mount
  useEffect(() => {
    loadModels();
    fetch(`${API_BASE}/skills`)
      .then((r) => (r.ok ? r.json() : { skills: [] }))
      .then((d) => setSkills(d.skills || []))
      .catch(() => setSkills([]));
    fetch(`${API_BASE}/llm/discover`)
      .then((r) => (r.ok ? r.json() : { providers: [] }))
      .then((d) => setProviderOk((d.providers || []).some((p: { detected: boolean }) => p.detected)))
      .catch(() => setProviderOk(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    try {
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages.slice(-HISTORY_CAP)));
    } catch {
      /* storage full or unavailable */
    }
  }, [messages]);

  const onSelectModel = (name: string) => {
    setSelectedModel(name);
    localStorage.setItem(CHAT_MODEL_KEY, name);
  };

  const onSelectPersonality = (name: string) => {
    setPersonality(name);
    localStorage.setItem(CHAT_PERSONALITY_KEY, name);
  };

  const systemPrompt = () => {
    const skillBlock =
      skills.length > 0
        ? `Available Resolve skills:\n${skills
            .map((s) => `- ${s.name} (${s.uri}): ${s.operations.join(", ")}`)
            .join("\n")}\n`
        : "";
    const persona = personality === "Custom" ? customPersonality : PERSONALITIES[personality] || "";
    return `${skillBlock}${persona}\nAlways ground answers in the listed skills and their operations.`.trim();
  };

  const sendMessage = async (override?: string) => {
    const text = (override ?? input).trim();
    if (!text || !selectedModel || loading) return;

    setInput("");
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    const assistantId = crypto.randomUUID();
    setMessages((prev) => [...prev, { id: assistantId, role: "assistant", content: "" }]);

    try {
      const res = await fetch(`${API_BASE}/llm/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: selectedModel, prompt: text, system: systemPrompt(), stream: true }),
      });
      if (!res.ok || !res.body) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const chunk = JSON.parse(line);
              if (chunk.error) throw new Error(chunk.error);
              if (chunk.response) {
                const token: string = chunk.response;
                setMessages((prev) =>
                  prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + token } : m)),
                );
              }
            } catch (e) {
              if (e instanceof Error && e.message !== "Unexpected end of JSON input") throw e;
              buffer = `${line}\n${buffer}`;
              break;
            }
          }
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generate failed");
      setMessages((prev) => prev.filter((m) => m.id !== assistantId || m.content !== ""));
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    try {
      localStorage.removeItem(CHAT_HISTORY_KEY);
    } catch {
      /* ignore */
    }
  };

  const exportChat = () => {
    const text = messages.map((m) => `${m.role.toUpperCase()}: ${m.content}`).join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "resolve-chat.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]" data-testid="chat-page">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2" data-testid="chat-controls">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">AI Video Editor</h2>
          <p className="text-slate-300">
            Chat with a local LLM (Ollama). Skills load automatically — pick a personality and model below.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            data-testid="chat-provider-status"
            title={providerOk === null ? "Probing providers" : providerOk ? "Local LLM detected" : "No local LLM"}
            className={`h-2.5 w-2.5 rounded-full ${
              providerOk === null ? "bg-slate-600 animate-pulse" : providerOk ? "bg-emerald-500" : "bg-red-500"
            }`}
          />
          <label className="text-slate-300 text-sm" htmlFor="chat-personality">
            Personality:
          </label>
          <select
            id="chat-personality"
            data-testid="personality-select"
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 text-sm min-w-[140px]"
            value={personality}
            onChange={(e) => onSelectPersonality(e.target.value)}
          >
            {Object.keys(PERSONALITIES).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <label className="text-slate-300 text-sm" htmlFor="chat-model">
            Model:
          </label>
          <select
            id="chat-model"
            data-testid="llm-model-select"
            className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 text-sm min-w-[160px]"
            value={selectedModel}
            onChange={(e) => onSelectModel(e.target.value)}
            disabled={loadingModels || models.length === 0}
          >
            {loadingModels && <option>Loading...</option>}
            {!loadingModels && models.length === 0 && <option>No models (start Ollama)</option>}
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          <Button
            data-testid="chat-export"
            variant="ghost"
            size="sm"
            onClick={exportChat}
            disabled={messages.length === 0}
            title="Export chat as .txt"
          >
            <Download className="w-4 h-4" />
          </Button>
          <Button
            data-testid="chat-clear"
            variant="ghost"
            size="sm"
            onClick={clearChat}
            disabled={messages.length === 0}
            title="Clear chat"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {personality === "Custom" && (
        <Input
          data-testid="chat-custom-personality"
          className="mb-2 bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
          placeholder="Describe your custom personality (e.g. terse finishing notes)"
          value={customPersonality}
          onChange={(e) => setCustomPersonality(e.target.value)}
        />
      )}

      {error && (
        <div className="mb-2 text-sm text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded px-3 py-2">
          {error}
        </div>
      )}

      <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col mb-4 overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="chat-messages">
          {messages.length === 0 && (
            <div>
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/30 shrink-0">
                  <Bot className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1 text-slate-300 text-sm">
                  {selectedModel
                    ? "Send a message to start, or try an example prompt below."
                    : "Select a model (or add one in Settings / Ollama) to chat."}
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2" data-testid="example-prompts">
                {EXAMPLE_PROMPTS.map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => sendMessage(p)}
                    disabled={!selectedModel || loading}
                    className="rounded-md border border-slate-700 bg-slate-900/60 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center border shrink-0 ${
                  msg.role === "assistant" ? "bg-blue-600/20 border-blue-500/30" : "bg-slate-800 border-slate-700"
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
          {loading && messages[messages.length - 1]?.role !== "assistant" && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/30 shrink-0">
                <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
              </div>
              <div className="text-slate-300 text-sm">Thinking...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </CardContent>

        <div className="p-4 border-t border-slate-800 bg-slate-900/20">
          <div className="flex gap-2">
            <Input
              data-testid="chat-input"
              className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
              placeholder="Ask the AI (e.g., suggest an edit or explain a step)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              disabled={!selectedModel || loading}
            />
            <Button
              data-testid="chat-send"
              className="bg-blue-600 hover:bg-blue-700"
              onClick={() => sendMessage()}
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
