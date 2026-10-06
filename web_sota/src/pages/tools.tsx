import { Palette, Play, Scissors } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function Tools() {
  return (
    <div className="space-y-6" data-testid="tools-page">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Production Tools</h2>
        <p className="text-slate-300">Advanced automation for DaVinci Resolve workflows</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3" data-testid="tools-grid">
        <Card className="border-slate-800 bg-slate-950/50" data-testid="tool-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Scissors className="h-5 w-5 text-blue-400" />
              Timeline Automator
            </CardTitle>
            <CardDescription className="text-slate-300">Perform batch cuts and clip additions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full bg-blue-600 hover:bg-blue-700">Open Timeline Editor</Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="tool-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Palette className="h-5 w-5 text-purple-400" />
              Color Grade Sync
            </CardTitle>
            <CardDescription className="text-slate-300">Apply and sync LUTs across timelines</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" className="w-full border-slate-800 text-slate-300">
              Sync Primary Nodes
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="tool-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Play className="h-5 w-5 text-emerald-400" />
              Render Queue
            </CardTitle>
            <CardDescription className="text-slate-300">Monitor and manage batch render jobs</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-300 mb-2">Open the Render Queue page for live job status.</p>
            <Button variant="ghost" className="w-full text-slate-300 hover:text-white">
              View Render Queue
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50" data-testid="tool-card">
          <CardHeader>
            <CardTitle className="text-white">Media Pool Operations</CardTitle>
            <CardDescription className="text-slate-300">Organize and search imported assets</CardDescription>
          </CardHeader>
          <CardContent className="flex gap-4">
            <Button variant="outline" className="flex-1 border-slate-800">
              Clear Unused Media
            </Button>
            <Button variant="outline" className="flex-1 border-slate-800">
              Verify Proxies
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50" data-testid="tool-card">
          <CardHeader>
            <CardTitle className="text-white">Project Manager</CardTitle>
            <CardDescription className="text-slate-300">Quick project switching and creation</CardDescription>
          </CardHeader>
          <CardContent className="flex gap-4">
            <Button variant="outline" className="flex-1 border-slate-800">
              List Projects
            </Button>
            <Button className="flex-1 bg-slate-800">New Setup</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
