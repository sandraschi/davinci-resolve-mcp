import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, GitMerge, Box, Cpu, Loader2 } from "lucide-react";

interface ResolveInfo {
    status: string;
    version?: string;
    project_name?: string | null;
    is_rendering?: boolean;
    message?: string;
}

export function Dashboard() {
    const [info, setInfo] = useState<ResolveInfo | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchInfo = async () => {
            try {
                const res = await fetch('/api/v1/resolve-info');
                const data = await res.json();
                setInfo(data);
            } catch {
                setInfo({ status: 'error', message: 'Connection failed' });
            } finally {
                setLoading(false);
            }
        };
        fetchInfo();
        const interval = setInterval(fetchInfo, 5000);
        return () => clearInterval(interval);
    }, []);

    const isConnected = info?.status === 'connected';
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Resolve Dashboard</h2>
                    <p className="text-slate-400">Media production and project status</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Active Project
                        </CardTitle>
                        <Cpu className={isConnected ? "h-4 w-4 text-emerald-500" : "h-4 w-4 text-slate-600"} />
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <Loader2 className="h-4 w-4 animate-spin text-slate-400 mt-2" />
                        ) : (
                            <>
                                <div className="text-xl font-bold text-white truncate h-8 mt-1" title={info?.project_name || 'None'}>
                                    {isConnected ? (info?.project_name || 'None') : 'Disconnected'}
                                </div>
                                <p className="text-xs text-slate-400 mt-1">
                                    Loaded in memory
                                </p>
                            </>
                        )}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Render Engine
                        </CardTitle>
                        <Activity className={info?.is_rendering ? "h-4 w-4 text-orange-500 animate-pulse" : "h-4 w-4 text-blue-500"} />
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <Loader2 className="h-4 w-4 animate-spin text-slate-400 mt-2" />
                        ) : (
                            <>
                                <div className="text-2xl font-bold text-white">
                                    {isConnected ? (info?.is_rendering ? 'Rendering' : 'Ready') : 'Offline'}
                                </div>
                                <p className="text-xs text-slate-400">
                                    GPU Accelerated
                                </p>
                            </>
                        )}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Resolve Version
                        </CardTitle>
                        <Box className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <Loader2 className="h-4 w-4 animate-spin text-slate-400 mt-2" />
                        ) : (
                            <>
                                <div className="text-xl font-bold text-white truncate h-8 mt-1">
                                    {isConnected ? info?.version : 'Unknown'}
                                </div>
                                <p className="text-xs text-slate-400 mt-1">
                                    Studio Edition
                                </p>
                            </>
                        )}
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            API Connection
                        </CardTitle>
                        <GitMerge className={isConnected ? "h-4 w-4 text-emerald-500" : "h-4 w-4 text-red-500"} />
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <Loader2 className="h-4 w-4 animate-spin text-slate-400 mt-2" />
                        ) : (
                            <>
                                <div className={isConnected ? "text-2xl font-bold text-emerald-400" : "text-2xl font-bold text-red-400"}>
                                    {isConnected ? 'Live' : 'Disconnected'}
                                </div>
                                <p className="text-xs text-slate-400">
                                    Scripting bridge {isConnected ? 'active' : 'inactive'}
                                </p>
                            </>
                        )}
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Production Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px] flex items-center justify-center border border-dashed border-slate-800 rounded-md bg-slate-900/20">
                            <span className="text-slate-500 text-sm">Real-time render & process graph placeholder</span>
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Active Production</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">Current Edit: Master_Commercial_v2</p>
                                    <p className="text-xs text-slate-400">Timeline: Color Grading Page</p>
                                </div>
                                <div className="ml-auto font-mono text-xs text-slate-400">04:21</div>
                            </div>
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2 bg-slate-700 rounded-full"></span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white text-opacity-50">Render Queue: Daily_Review_0216</p>
                                    <p className="text-xs text-slate-500">Scheduled for 16:30</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
