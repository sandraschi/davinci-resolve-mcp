import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MonitorPlay, ListVideo } from "lucide-react";

export function Render() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Render Queue</h2>
                    <p className="text-slate-400">Monitor and manage render jobs</p>
                </div>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <MonitorPlay className="h-5 w-5 text-orange-500" /> Active Jobs
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="p-12 text-center border-2 border-dashed border-slate-800 rounded-lg">
                        <ListVideo className="h-10 w-10 text-slate-600 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-300">Render Queue Empty</h3>
                        <p className="text-sm text-slate-500 mt-2">The DaVinci Resolve render queue is currently unpopulated or rendering is not in progress.</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
