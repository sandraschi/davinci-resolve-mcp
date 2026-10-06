import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface InboxEntry {
  id: string;
  timestamp: string;
  level: string;
  kind: string;
  detail: string;
}

/**
 * Inbox: warnings and errors from the server log ring buffer.
 * A live event surface for operators (failed tool calls, disconnects).
 */
export function Inbox() {
  const [entries, setEntries] = useState<InboxEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInbox = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ limit: "50", sort: "desc" });
      const res = await fetch(`/api/v1/logs?${params}`);
      if (!res.ok) throw new Error("Failed to fetch events");
      const data = await res.json();
      const items: InboxEntry[] = (data.entries || []).filter(
        (e: InboxEntry) => e.level === "WARNING" || e.level === "ERROR",
      );
      setEntries(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInbox();
    const t = setInterval(fetchInbox, 15000);
    return () => clearInterval(t);
  }, [fetchInbox]);

  return (
    <div className="space-y-6" data-testid="inbox-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Inbox</h2>
          <p className="text-slate-300">Warnings and errors from the server log</p>
        </div>
        <button
          type="button"
          data-testid="inbox-refresh"
          onClick={fetchInbox}
          className="rounded-md border border-slate-700 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-300" data-testid="inbox-loading">
          Loading events...
        </div>
      ) : error ? (
        <div
          className="p-8 text-center border border-slate-800 bg-slate-900/50 rounded-lg text-slate-300"
          data-testid="inbox-error"
        >
          <p className="text-red-400 mb-2">Error loading inbox</p>
          <p className="text-sm">{error}</p>
        </div>
      ) : entries.length === 0 ? (
        <div className="text-slate-300 italic p-4 border border-slate-800 rounded-md" data-testid="inbox-empty">
          All quiet — no warnings or errors recorded.
        </div>
      ) : (
        <Card className="border-slate-800 bg-slate-950/50" data-testid="inbox-list">
          <CardHeader>
            <CardTitle className="text-white text-base">{entries.length} events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {entries.map((e) => (
                <div
                  key={e.id}
                  data-testid="inbox-event"
                  className="flex items-start gap-3 rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2"
                >
                  <span
                    className={`shrink-0 rounded px-1.5 py-0.5 text-sm font-bold ${
                      e.level === "ERROR" ? "text-red-400 bg-red-950/40" : "text-yellow-400 bg-yellow-950/40"
                    }`}
                  >
                    {e.level}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm text-slate-200 break-words">{e.detail}</p>
                    <p className="font-mono text-sm text-slate-400">
                      {e.timestamp} · {e.kind}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
