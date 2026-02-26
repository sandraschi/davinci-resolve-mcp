import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, Box, Loader2, Play } from "lucide-react";

interface TimelineInfo {
    name: string;
    start_code: string;
    track_count_video: number;
    track_count_audio: number;
}

interface TimelineResponse {
    timeline: TimelineInfo | null;
}

export function Timeline() {
    const [data, setData] = useState<TimelineResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTimeline = async () => {
            try {
                const response = await fetch('/api/v1/timeline');
                if (!response.ok) throw new Error('Failed to fetch timeline');
                const result = await response.json();
                setData(result);
            } catch (err) {
                if (err instanceof Error) setError(err.message);
                else setError('Connection error');
            } finally {
                setLoading(false);
            }
        };

        fetchTimeline();
    }, []);

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-6">
                <h2 className="text-2xl font-bold tracking-tight text-white">Timeline inspector</h2>
                <div className="p-8 text-center border border-slate-800 bg-slate-900/50 rounded-lg text-slate-400">
                    <p className="text-red-400 mb-2">Error connecting to Resolve API</p>
                    <p className="text-sm">{error}</p>
                </div>
            </div>
        );
    }

    const { timeline } = data || {};

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Timeline Inspector</h2>
                    <p className="text-slate-400">Current timeline metadata and tracks</p>
                </div>
            </div>

            {!timeline ? (
                <div className="p-12 text-center border border-slate-800 bg-slate-950/50 rounded-lg">
                    <Clock className="h-10 w-10 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-300">No active timeline</h3>
                    <p className="text-sm text-slate-500 mt-2">Open a timeline in DaVinci Resolve to see details here.</p>
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2">
                    <Card className="border-blue-500/20 bg-blue-950/10 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-white">
                                <Play className="h-5 w-5 text-blue-500" />
                                {timeline.name}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center py-2 border-b border-slate-800">
                                    <span className="text-slate-400 text-sm">Start Timecode</span>
                                    <span className="text-white font-mono bg-slate-900 px-2 py-1 rounded">{timeline.start_code}</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-slate-800">
                                    <span className="text-slate-400 text-sm flex items-center gap-2"><Box className="h-4 w-4 text-purple-400" /> Video Tracks</span>
                                    <span className="text-white font-medium">{timeline.track_count_video}</span>
                                </div>
                                <div className="flex justify-between items-center py-2">
                                    <span className="text-slate-400 text-sm flex items-center gap-2"><Clock className="h-4 w-4 text-emerald-400" /> Audio Tracks</span>
                                    <span className="text-white font-medium">{timeline.track_count_audio}</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
