import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FolderOpen, Clock, Play } from "lucide-react";

interface ProjectResponse {
    current_project: string | null;
    projects: string[];
}

export function Projects() {
    const [data, setData] = useState<ProjectResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                // The Vite proxy defaults to 8000 but our backend is 10843. 
                // Using relative path assuming vite.config.ts has a proxy setup or using absolute if not. 
                // In SOTA, there's usually a proxy. Let's try relative first.
                const response = await fetch('/api/v1/projects');
                if (!response.ok) throw new Error('Failed to fetch projects');
                const result = await response.json();
                setData(result);
            } catch (err) {
                if (err instanceof Error) setError(err.message);
                else setError('Connection error');
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, []);

    if (loading) {
        return <div className="p-8 text-center text-slate-400">Loading projects...</div>;
    }

    if (error) {
        return (
            <div className="space-y-6">
                <h2 className="text-2xl font-bold tracking-tight text-white">Projects</h2>
                <div className="p-8 text-center border border-slate-800 bg-slate-900/50 rounded-lg text-slate-400">
                    <p className="text-red-400 mb-2">Error connecting to Resolve API</p>
                    <p className="text-sm">{error}</p>
                    <p className="text-sm mt-4">Make sure DaVinci Resolve is running and scripting is enabled.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Project Library</h2>
                    <p className="text-slate-400">Manage and explore loaded projects</p>
                </div>
            </div>

            {data?.current_project && (
                <div className="mb-8">
                    <h3 className="text-lg font-medium text-slate-200 mb-4 flex items-center gap-2">
                        <Play className="h-5 w-5 text-emerald-500" /> Active Project
                    </h3>
                    <Card className="border-emerald-500/30 bg-emerald-950/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-xl text-white">{data.current_project}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-slate-400">Currently loaded sequence and media.</p>
                        </CardContent>
                    </Card>
                </div>
            )}

            <div>
                <h3 className="text-lg font-medium text-slate-200 mb-4 flex items-center gap-2">
                    <FolderOpen className="h-5 w-5 text-blue-500" /> Available Projects
                </h3>

                {(!data?.projects || data.projects.length === 0) ? (
                    <div className="text-slate-500 italic p-4 border border-slate-800 rounded-md">
                        No projects found in the current folder.
                    </div>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {data.projects.map((proj, i) => (
                            <Card key={i} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/80 transition-colors cursor-pointer group">
                                <CardHeader className="pb-2">
                                    <div className="flex items-start justify-between">
                                        <CardTitle className="text-md text-white group-hover:text-blue-400 transition-colors">
                                            {proj}
                                        </CardTitle>
                                        <FolderOpen className="h-4 w-4 text-slate-600 group-hover:text-blue-500 transition-colors" />
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-xs text-slate-500 flex items-center gap-1">
                                        <Clock className="h-3 w-3" /> Last accessed recently
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
