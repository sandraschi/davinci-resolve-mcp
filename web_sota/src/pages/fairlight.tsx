import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Music2, Volume2, VolumeX, Mic, MicOff } from 'lucide-react';

const API_BASE = '/api/v1';

interface FairlightTrack {
    index: number;
    name: string;
    muted: boolean;
    solo: boolean;
    locked: boolean;
}

interface FairlightTracksResponse {
    status?: string;
    timeline_name?: string;
    track_count?: number;
    tracks?: FairlightTrack[];
}

export function Fairlight() {
    const [data, setData] = useState<FairlightTracksResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

    const fetchTracks = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE}/fairlight/tracks`);
            if (!res.ok) throw new Error(await res.text());
            const result = await res.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTracks();
    }, []);

    const openPage = async () => {
        setActionLoading((prev) => ({ ...prev, openPage: true }));
        try {
            const res = await fetch(`${API_BASE}/fairlight/open-page`, { method: 'POST' });
            if (!res.ok) throw new Error(await res.text());
            await res.json();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Open page failed');
        } finally {
            setActionLoading((prev) => ({ ...prev, openPage: false }));
        }
    };

    const setMute = async (trackIndex: number, mute: boolean) => {
        const key = `mute-${trackIndex}`;
        setActionLoading((prev) => ({ ...prev, [key]: true }));
        try {
            const res = await fetch(
                `${API_BASE}/fairlight/track/mute?track_index=${trackIndex}&mute=${mute}`,
                { method: 'POST' }
            );
            if (!res.ok) throw new Error(await res.text());
            await fetchTracks();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Set mute failed');
        } finally {
            setActionLoading((prev) => ({ ...prev, [key]: false }));
        }
    };

    const setSolo = async (trackIndex: number, solo: boolean) => {
        const key = `solo-${trackIndex}`;
        setActionLoading((prev) => ({ ...prev, [key]: true }));
        try {
            const res = await fetch(
                `${API_BASE}/fairlight/track/solo?track_index=${trackIndex}&solo=${solo}`,
                { method: 'POST' }
            );
            if (!res.ok) throw new Error(await res.text());
            await fetchTracks();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Set solo failed');
        } finally {
            setActionLoading((prev) => ({ ...prev, [key]: false }));
        }
    };

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        <Music2 className="h-7 w-7 text-amber-500" />
                        Fairlight
                    </h2>
                    <p className="text-slate-400">DAW / audio page: tracks, mute, solo</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={openPage}
                        disabled={actionLoading.openPage}
                        className="border-slate-600 text-slate-300 hover:bg-slate-800"
                    >
                        {actionLoading.openPage ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                            'Open Fairlight page in Resolve'
                        )}
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={fetchTracks}
                        className="border-slate-600 text-slate-300 hover:bg-slate-800"
                    >
                        Refresh
                    </Button>
                </div>
            </div>

            {error && (
                <div className="rounded-lg border border-red-900/50 bg-red-950/20 p-4 text-red-300 text-sm">
                    {error}
                </div>
            )}

            {data?.status === 'disconnected' && (
                <Card className="border-slate-800 bg-slate-900/50">
                    <CardContent className="pt-6">
                        <p className="text-slate-400">Not connected to DaVinci Resolve. Start Resolve and ensure the MCP backend is connected.</p>
                    </CardContent>
                </Card>
            )}

            {data?.tracks && data.tracks.length > 0 && (
                <Card className="border-amber-500/20 bg-slate-900/50">
                    <CardHeader>
                        <CardTitle className="text-white">
                            Timeline: {data.timeline_name ?? 'Current'} — {data.track_count} audio tracks
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {data.tracks.map((track) => (
                                <div
                                    key={track.index}
                                    className="flex items-center gap-4 rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3"
                                >
                                    <span className="w-8 text-slate-400 font-mono text-sm">{track.index}</span>
                                    <span className="flex-1 font-medium text-slate-200 truncate">{track.name}</span>
                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className={track.muted ? 'text-red-400' : 'text-slate-400'}
                                            onClick={() => setMute(track.index, !track.muted)}
                                            disabled={actionLoading[`mute-${track.index}`]}
                                        >
                                            {track.muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className={track.solo ? 'text-amber-400' : 'text-slate-400'}
                                            onClick={() => setSolo(track.index, !track.solo)}
                                            disabled={actionLoading[`solo-${track.index}`]}
                                        >
                                            {track.solo ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
                                        </Button>
                                    </div>
                                    {track.locked && (
                                        <span className="text-xs text-slate-500">Locked</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {data?.tracks && data.tracks.length === 0 && data.status === 'success' && (
                <Card className="border-slate-800 bg-slate-900/50">
                    <CardContent className="pt-6">
                        <p className="text-slate-400">No audio tracks in current timeline.</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
