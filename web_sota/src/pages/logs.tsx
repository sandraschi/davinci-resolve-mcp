import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Terminal } from "lucide-react";

export function Logs() {
    return (
        <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
            <h2 className="text-2xl font-bold tracking-tight text-white">System Logs</h2>
            <Card className="border-slate-800 bg-slate-950/50 flex-1 overflow-hidden flex flex-col font-mono text-sm">
                <CardHeader className="bg-slate-900/30 border-b border-slate-800 py-2">
                    <div className="flex items-center gap-2 text-slate-400 text-xs">
                        <Terminal className="h-4 w-4" />
                        resolve_mcp_bridge.log
                    </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto p-4 text-slate-300">
                    <p className="text-slate-500">[15:39:17] INFO: Resolve MCP Bridge Initialized</p>
                    <p className="text-slate-500">[15:39:18] DEBUG: Connection to Resolve API established</p>
                    <p className="text-emerald-400">[15:39:20] SUCCESS: Project 'Vienna_Aesthetics' loaded</p>
                    <p className="text-blue-400">[15:39:25] INFO: Listening on port 10842</p>
                    <div className="animate-pulse">_</div>
                </CardContent>
            </Card>
        </div>
    );
}
