import { useEffect, useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Terminal, Loader2, RefreshCw } from 'lucide-react';

const API_BASE = '/api/v1';

interface LogEntry {
    id: string;
    ts: string;
    level: string;
    name: string;
    message: string;
    exc?: string | null;
}

interface LogsResponse {
    entries: LogEntry[];
    count: number;
}

const levelClass: Record<string, string> = {
    debug: 'text-slate-500',
    info: 'text-slate-300',
    warn: 'text-amber-400',
    error: 'text-red-400',
};

export function Logs() {
    const [data, setData] = useState<LogsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [autoRefresh, setAutoRefresh] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    const fetchLogs = async () => {
        try {
            const res = await fetch(`${API_BASE}/logs`);
            if (!res.ok) throw new Error(await res.text());
            const result: LogsResponse = await res.json();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch logs');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    useEffect(() => {
        if (!autoRefresh) return;
        const id = setInterval(fetchLogs, 2000);
        return () => clearInterval(id);
    }, [autoRefresh]);

    useEffect(() => {
        if (autoRefresh && data?.entries?.length) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [autoRefresh, data?.entries?.length]);

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
            </div>
        );
    }

    return (
        <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight text-white">System Logs</h2>
                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        onClick={() => setAutoRefresh((v) => !v)}
                        className={`rounded border px-3 py-1.5 text-sm ${autoRefresh ? 'border-amber-500/50 bg-amber-950/30 text-amber-300' : 'border-slate-600 text-slate-400 hover:bg-slate-800'}`}
                    >
                        {autoRefresh ? 'Pause' : 'Auto-refresh'}
                    </button>
                    <button
                        type="button"
                        onClick={() => { setLoading(true); fetchLogs(); }}
                        className="flex items-center gap-1.5 rounded border border-slate-600 px-3 py-1.5 text-sm text-slate-400 hover:bg-slate-800"
                    >
                        <RefreshCw className="h-4 w-4" /> Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="rounded-lg border border-red-900/50 bg-red-950/20 p-4 text-red-300 text-sm">
                    {error}
                </div>
            )}

            <Card className="border-slate-800 bg-slate-950/50 flex-1 overflow-hidden flex flex-col font-mono text-sm">
                <CardHeader className="bg-slate-900/30 border-b border-slate-800 py-2">
                    <div className="flex items-center gap-2 text-slate-400 text-xs">
                        <Terminal className="h-4 w-4" />
                        Server log buffer ({data?.count ?? 0} entries)
                    </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto p-4 text-slate-300 min-h-0">
                    {data?.entries && data.entries.length > 0 ? (
                        <div className="space-y-0.5">
                            {data.entries.map((entry) => (
                                <div
                                    key={entry.id}
                                    className={`flex gap-2 break-all ${levelClass[entry.level] ?? 'text-slate-400'}`}
                                >
                                    <span className="text-slate-600 shrink-0">[{entry.ts}]</span>
                                    <span className="shrink-0 uppercase text-xs w-12">{entry.level}</span>
                                    <span className="truncate shrink-0 max-w-[120px] text-slate-500" title={entry.name}>
                                        {entry.name.split('.').pop()}
                                    </span>
                                    <span className="min-w-0">{entry.message}</span>
                                    {entry.exc && (
                                        <pre className="mt-1 w-full text-red-300/90 text-xs whitespace-pre-wrap">
                                            {entry.exc}
                                        </pre>
                                    )}
                                </div>
                            ))}
                            <div ref={bottomRef} />
                        </div>
                    ) : (
                        <p className="text-slate-500">No log entries yet. Use the app to generate activity.</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
