import { Play, RefreshCw, Scissors } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function Actions() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Production Actions</h2>
        <p className="text-slate-400">Rapid timeline and media management</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white text-base">
              <Play className="h-4 w-4 text-emerald-400" />
              Render Active Timeline
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Queue the current timeline to the Render Queue immediately.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full bg-emerald-600 hover:bg-emerald-700">Quick Render</Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white text-base">
              <Scissors className="h-4 w-4 text-amber-400" />
              Auto-Cut Scene
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Apply scene cut detection to the selected clip.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full border-slate-800 text-amber-400 hover:bg-amber-950/30">
              Start Analysis
            </Button>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white text-base">
              <RefreshCw className="h-4 w-4 text-blue-400" />
              Relink Media
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Scan project paths and relink missing assets from source disk.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full border-slate-800 text-blue-400 hover:bg-blue-950/30">
              Scan & Relink
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
