import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/common/utils';
import {
    Workflow, Zap, Layers, Wand2, Cog, Film, Music2, Palette,
    Subtitles, FolderOpen, MonitorPlay, Brain, Terminal, Play,
    Download, Upload, Clock, CheckCircle2, Loader2, AlertCircle, Sparkles
} from 'lucide-react';

interface WorkflowStep {
    tool: string;
    action: string;
    description: string;
    icon: typeof Workflow;
    params?: string;
}

interface WorkflowDemo {
    id: string;
    title: string;
    description: string;
    category: string;
    steps: WorkflowStep[];
    cli_example?: string;
    portmanteau_example?: string;
}

const workflows: WorkflowDemo[] = [
    {
        id: 'import-grade-export',
        title: 'Import → Grade → Export',
        description: 'Full pipeline: import media, color grade with LUTs, render final output',
        category: 'core',
        steps: [
            { tool: 'resolve_media', action: 'import', description: 'Import raw footage', icon: Upload },
            { tool: 'resolve_timeline', action: 'create', description: 'Create edit timeline', icon: Clock },
            { tool: 'resolve_timeline', action: 'add_clip', description: 'Add clips to timeline', icon: Film },
            { tool: 'resolve_color', action: 'apply_lut', description: 'Apply creative LUT', icon: Palette },
            { tool: 'resolve_color', action: 'adjust_wheels', description: 'Fine-tune color wheels', icon: Palette },
            { tool: 'resolve_render', action: 'timeline', description: 'Render final output', icon: MonitorPlay },
        ],
        cli_example: `davinci-resolve-mcp open-project "My Film"
davinci-resolve-mcp import-media C:/footage/*.mp4
davinci-resolve-mcp render C:/output/ --timeline "Main Edit" --format mp4`,
        portmanteau_example: `resolve_system("host_launch")
resolve_project("create", name="My Film", width=3840, height=2160)
resolve_media("import", paths=["C:/footage/scene1.mp4"])
resolve_timeline("create", name="Main Edit")
resolve_timeline("add_clip", clip_path="scene1.mp4")
resolve_color("apply_lut", lut_path="C:/LUTs/Film.cube")
resolve_render("timeline", output_path="C:/output/")`,
    },
    {
        id: 'fairlight-mix',
        title: 'Fairlight Audio Mix',
        description: 'Open Fairlight, configure EQ, set sends, render with audio processing',
        category: 'audio',
        steps: [
            { tool: 'resolve_fairlight', action: 'open_page', description: 'Open Fairlight page', icon: Music2 },
            { tool: 'resolve_fairlight', action: 'track_eq', description: 'Set EQ on dialogue track', icon: Music2, params: 'Band 1, -3dB, 200Hz' },
            { tool: 'resolve_fairlight', action: 'track_send', description: 'Send to reverb bus', icon: Music2 },
            { tool: 'resolve_audio', action: 'normalize', description: 'Normalize to -23 LUFS', icon: Music2 },
            { tool: 'resolve_render', action: 'timeline', description: 'Export with mastered audio', icon: MonitorPlay },
        ],
        portmanteau_example: `resolve_fairlight("open_page")
resolve_fairlight("track_eq", track_index=1, eq_band=1, eq_gain_db=-3, eq_frequency=200)
resolve_fairlight("track_send", track_index=1, bus_index=1, send_level=0.75)
resolve_audio("normalize", target_level=-23.0)`,
    },
    {
        id: 'subtitle-workflow',
        title: 'Subtitle Management',
        description: 'Import SRT, edit subtitles, adjust timing, export',
        category: 'media',
        steps: [
            { tool: 'resolve_subtitle', action: 'import_srt', description: 'Load SRT file', icon: Subtitles },
            { tool: 'resolve_subtitle', action: 'get', description: 'Review all subtitles', icon: Subtitles },
            { tool: 'resolve_subtitle', action: 'edit', description: 'Fix timing/text', icon: Subtitles },
            { tool: 'resolve_subtitle', action: 'export_srt', description: 'Export finalized SRT', icon: Subtitles },
        ],
        cli_example: `davinci-resolve-mcp import-media --project "My Film"`,
        portmanteau_example: `resolve_subtitle("import_srt", srt_path="C:/captions.srt")
resolve_subtitle("edit", subtitle_index=3, text="Corrected text")
resolve_subtitle("export_srt", output_path="C:/final.srt")`,
    },
    {
        id: 'stills-versioning',
        title: 'Gallery & Grade Versioning',
        description: 'Grab stills, compare grades, apply grades across shots',
        category: 'color',
        steps: [
            { tool: 'resolve_color', action: 'grab_still', description: 'Grab reference still', icon: Palette },
            { tool: 'resolve_color', action: 'adjust_wheels', description: 'Try alternate grade', icon: Palette },
            { tool: 'resolve_color', action: 'grab_still', description: 'Grab version 2', icon: Palette },
            { tool: 'resolve_color', action: 'get_stills', description: 'Compare versions', icon: Palette },
            { tool: 'resolve_color', action: 'apply_grade_from_still', description: 'Apply chosen grade', icon: Palette },
        ],
        portmanteau_example: `resolve_color("grab_still", still_name="Reference Grade")
resolve_color("adjust_wheels", lift={"r": 0.05, "b": -0.03})
resolve_color("grab_still", still_name="Warm Grade")
resolve_color("get_stills")
resolve_color("apply_grade_from_still", still_index=1)`,
    },
    {
        id: 'marker-keyframe',
        title: 'Markers & Keyframe Animation',
        description: 'Place timeline markers, animate clip properties with keyframes',
        category: 'timeline',
        steps: [
            { tool: 'resolve_timeline', action: 'add_marker', description: 'Place VFX marker', icon: Clock, params: 'frame 120, Red' },
            { tool: 'resolve_timeline', action: 'add_keyframe', description: 'Keyframe zoom at 0', icon: Clock, params: 'Zoom=1.0' },
            { tool: 'resolve_timeline', action: 'add_keyframe', description: 'Keyframe zoom at 48', icon: Clock, params: 'Zoom=1.5' },
            { tool: 'resolve_timeline', action: 'get_keyframes', description: 'Verify animation curve', icon: Clock },
            { tool: 'resolve_timeline', action: 'get_markers', description: 'Review marker list', icon: Clock },
        ],
        portmanteau_example: `resolve_timeline("add_marker", frame=120, color="Red", name="VFX cue")
resolve_timeline("add_keyframe", property_name="Zoom", frame=0, value=1.0)
resolve_timeline("add_keyframe", property_name="Zoom", frame=48, value=1.5)
resolve_timeline("get_keyframes", property_name="Zoom")`,
    },
    {
        id: 'batch-render',
        title: 'Batch Operations',
        description: 'Process multiple timelines, check status, handle failures',
        category: 'core',
        steps: [
            { tool: 'resolve_project', action: 'open', description: 'Open project', icon: FolderOpen },
            { tool: 'resolve_render', action: 'timeline', description: 'Render Timeline A', icon: MonitorPlay },
            { tool: 'resolve_render', action: 'timeline', description: 'Render Timeline B', icon: MonitorPlay },
            { tool: 'resolve_render', action: 'job_status', description: 'Check all jobs', icon: MonitorPlay },
        ],
        cli_example: `davinci-resolve-mcp render C:/output/ -t "Timeline A"
davinci-resolve-mcp render C:/output/ -t "Timeline B"`,
    },
    {
        id: 'cli-automation',
        title: 'CLI Script Automation',
        description: 'Run custom Python scripts with full Resolve API access',
        category: 'cli',
        steps: [
            { tool: 'CLI', action: 'open-project', description: 'Open target project', icon: Terminal },
            { tool: 'CLI', action: 'import-media', description: 'Import source media', icon: Terminal },
            { tool: 'CLI', action: 'run-script', description: 'Execute custom script', icon: Terminal },
            { tool: 'CLI', action: 'render', description: 'Export final output', icon: Terminal },
        ],
        cli_example: `davinci-resolve-mcp open-project "My Project" --create
davinci-resolve-mcp import-media C:/footage/*.mp4
davinci-resolve-mcp run-script my_custom_grade.py --project "My Project"
davinci-resolve-mcp render C:/output/ --timeline "Final" --codec prores_422_hq`,
    },
];

const categoryColors: Record<string, string> = {
    core: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    color: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    audio: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    timeline: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    media: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    cli: 'bg-slate-500/10 text-slate-300 border-slate-500/20',
};

const toolIcons: Record<string, typeof Workflow> = {
    resolve_media: Upload,
    resolve_timeline: Clock,
    resolve_color: Palette,
    resolve_render: MonitorPlay,
    resolve_audio: Music2,
    resolve_fairlight: Music2,
    resolve_subtitle: Subtitles,
    resolve_project: FolderOpen,
    resolve_system: Cog,
    CLI: Terminal,
};

export function Workflows() {
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDemo | null>(null);
    const [demoStep, setDemoStep] = useState(-1);
    const [demoRunning, setDemoRunning] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading');

    useEffect(() => {
        fetch('/api/v1/resolve-info')
            .then(r => r.json())
            .then(d => setConnectionStatus(d.version ? 'connected' : 'disconnected'))
            .catch(() => setConnectionStatus('disconnected'));
    }, []);

    const categories = ['all', ...new Set(workflows.map(w => w.category))];
    const filtered = selectedCategory === 'all'
        ? workflows
        : workflows.filter(w => w.category === selectedCategory);

    const runDemo = async (workflow: WorkflowDemo) => {
        setSelectedWorkflow(workflow);
        setDemoRunning(true);
        setDemoStep(-1);
        for (let i = 0; i < workflow.steps.length; i++) {
            setDemoStep(i);
            await new Promise(r => setTimeout(r, 800));
        }
        setDemoRunning(false);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
                        <Brain className="h-7 w-7 text-blue-400" />
                        AI Workflows
                    </h2>
                    <p className="text-slate-400 mt-1">
                        Agentic orchestration patterns for DaVinci Resolve automation
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    {connectionStatus === 'loading' ? (
                        <Badge className="border-slate-700 text-slate-400">
                            <Loader2 className="h-3 w-3 mr-1 animate-spin" /> Checking
                        </Badge>
                    ) : connectionStatus === 'connected' ? (
                        <Badge className="border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                            <CheckCircle2 className="h-3 w-3 mr-1" /> Connected
                        </Badge>
                    ) : (
                        <Badge className="border-red-500/30 text-red-400 bg-red-500/10">
                            <AlertCircle className="h-3 w-3 mr-1" /> Disconnected
                        </Badge>
                    )}
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: 'Portmanteau Tools', value: '9', icon: Layers, color: 'text-blue-400' },
                    { label: 'Individual Tools', value: '38', icon: Wand2, color: 'text-purple-400' },
                    { label: 'CLI Commands', value: '7', icon: Terminal, color: 'text-emerald-400' },
                    { label: 'API Coverage', value: '~65%', icon: Zap, color: 'text-amber-400' },
                ].map((stat) => (
                    <Card key={stat.label} className="border-slate-800 bg-slate-950/50">
                        <CardContent className="p-4 flex items-center gap-3">
                            <stat.icon className={cn("h-5 w-5", stat.color)} />
                            <div>
                                <p className="text-2xl font-bold text-white">{stat.value}</p>
                                <p className="text-xs text-slate-400">{stat.label}</p>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Workflow Catalog */}
            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="text-white flex items-center gap-2">
                                <Workflow className="h-5 w-5 text-blue-400" />
                                Workflow Catalog
                            </CardTitle>
                            <CardDescription>Pre-built automation recipes for common production tasks</CardDescription>
                        </div>
                        <div className="flex gap-1">
                            {categories.map(cat => (
                                <button
                                    key={cat}
                                    onClick={() => {
                                        setSelectedCategory(cat);
                                        setSelectedWorkflow(null);
                                        setDemoRunning(false);
                                    }}
                                    className={cn(
                                        "px-3 py-1 rounded-md text-xs font-medium transition-colors capitalize",
                                        selectedCategory === cat
                                            ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                                            : "text-slate-400 hover:text-white hover:bg-slate-800"
                                    )}
                                >
                                    {cat}
                                </button>
                            ))}
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {filtered.map((workflow) => (
                            <div
                                key={workflow.id}
                                onClick={() => runDemo(workflow)}
                                className={cn(
                                    "p-4 rounded-lg border cursor-pointer transition-all hover:bg-slate-800/50",
                                    selectedWorkflow?.id === workflow.id
                                        ? "border-blue-500/30 bg-slate-800/50"
                                        : "border-slate-800 bg-slate-950/30"
                                )}
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <Badge className={cn("text-xs border", categoryColors[workflow.category] || categoryColors.core)}>
                                            {workflow.category}
                                        </Badge>
                                        <span className="font-medium text-white">{workflow.title}</span>
                                    </div>
                                    <span className="text-xs text-slate-500">{workflow.steps.length} steps</span>
                                </div>
                                <p className="text-sm text-slate-400 mb-3">{workflow.description}</p>

                                {/* Animated step progression */}
                                {selectedWorkflow?.id === workflow.id && (
                                    <div className="space-y-2 mt-3 pt-3 border-t border-slate-800">
                                        <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                                            {demoRunning ? (
                                                <><Loader2 className="h-3 w-3 animate-spin" /> Running workflow...</>
                                            ) : (
                                                <><CheckCircle2 className="h-3 w-3 text-emerald-400" /> Demo complete — ready to run for real</>
                                            )}
                                        </div>
                                        <Progress value={demoStep >= 0 ? ((demoStep + 1) / workflow.steps.length) * 100 : 0} className="h-1" />
                                        <div className="grid grid-cols-5 gap-1 mt-1">
                                            {workflow.steps.map((step, i) => {
                                                const Icon = toolIcons[step.tool] || Cog;
                                                const done = i <= demoStep;
                                                return (
                                                    <div key={i} className={cn(
                                                        "flex flex-col items-center p-2 rounded text-center transition-all duration-300",
                                                        done ? "text-white" : "text-slate-600"
                                                    )}>
                                                        <Icon className={cn("h-4 w-4 mb-1", done ? step.tool === 'CLI' ? "text-slate-300" : "text-blue-400" : "")} />
                                                        <span className="text-[10px] leading-tight">{step.action}</span>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Two-column detail panels */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Portmanteau Tools Panel */}
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Sparkles className="h-5 w-5 text-amber-400" />
                            Portmanteau API Reference
                        </CardTitle>
                        <CardDescription>Single-tool multi-action pattern — 9 tools covering 38+ operations</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-72">
                            <div className="space-y-2 pr-3">
                                {[
                                    { tool: 'resolve_project', actions: ['create', 'open', 'list', 'get_settings', 'update_settings'] },
                                    { tool: 'resolve_media', actions: ['import', 'list', 'create_folder', 'get_metadata'] },
                                    { tool: 'resolve_timeline', actions: ['create', 'info', 'add_clip', 'cut', 'set_playhead', 'add_marker', 'get_markers', 'delete_marker', 'add_keyframe', 'get_keyframes', 'delete_keyframe', 'set_clip_property'] },
                                    { tool: 'resolve_color', actions: ['create_node', 'apply_lut', 'set_color_space', 'adjust_wheels', 'grab_still', 'get_stills', 'apply_grade_from_still'] },
                                    { tool: 'resolve_render', actions: ['timeline', 'presets', 'with_preset', 'job_status'] },
                                    { tool: 'resolve_audio', actions: ['get_tracks', 'add_effect', 'adjust_levels', 'normalize'] },
                                    { tool: 'resolve_fairlight', actions: ['open_page', 'get_tracks', 'set_mute', 'set_solo', 'set_volume', 'track_eq', 'track_send', 'get_buses', 'track_automation'] },
                                    { tool: 'resolve_subtitle', actions: ['add', 'get', 'edit', 'delete', 'import_srt', 'export_srt'] },
                                    { tool: 'resolve_system', actions: ['info', 'status', 'health', 'help', 'host_status', 'host_launch'] },
                                ].map(({ tool, actions }) => (
                                    <div key={tool} className="flex items-start gap-2 p-2 rounded hover:bg-slate-800/50 transition-colors">
                                        <code className="text-xs font-mono text-emerald-400 whitespace-nowrap min-w-[170px]">{tool}</code>
                                        <div className="flex flex-wrap gap-1">
                                            {actions.map(a => (
                                                <code key={a} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">{a}</code>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>

                {/* CLI Commands Panel */}
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Terminal className="h-5 w-5 text-emerald-400" />
                            CLI Command Reference
                        </CardTitle>
                        <CardDescription>Direct terminal access to Resolve operations</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-72">
                            <div className="space-y-3 pr-3">
                                {[
                                    { cmd: 'davinci-resolve-mcp', desc: 'Start MCP server (stdio for Claude Desktop/Cursor)' },
                                    { cmd: 'davinci-resolve-mcp start', desc: 'Start HTTP MCP server on port 8000' },
                                    { cmd: 'davinci-resolve-mcp web', desc: 'Start webapp API backend on port 10843' },
                                    { cmd: 'davinci-resolve-mcp check', desc: 'Verify Resolve installation and connection' },
                                    { cmd: 'davinci-resolve-mcp run-script <script.py>', desc: 'Execute arbitrary Resolve Python script' },
                                    { cmd: 'davinci-resolve-mcp render <output>', desc: 'Render timeline from CLI (--timeline, --format, --codec)' },
                                    { cmd: 'davinci-resolve-mcp import-media <paths...>', desc: 'Import media files (--folder, --list)' },
                                    { cmd: 'davinci-resolve-mcp open-project <name>', desc: 'Open/create project (--create)' },
                                ].map(({ cmd, desc }) => (
                                    <div key={cmd} className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                                        <code className="text-xs font-mono text-cyan-400 block mb-1">{cmd}</code>
                                        <p className="text-xs text-slate-400">{desc}</p>
                                    </div>
                                ))}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>

            {/* Latest Additions */}
            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Zap className="h-5 w-5 text-amber-400" />
                        What's New in 0.3.0
                    </CardTitle>
                    <CardDescription>Recently added capabilities and gap coverage</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[
                            { title: 'Markers', desc: 'Add/get/delete timeline markers with 16 colors, names, notes, and duration', icon: Clock },
                            { title: 'Keyframes', desc: 'Add/delete/get keyframes on clip properties (Zoom, Position, Speed)', icon: Play },
                            { title: 'Subtitles', desc: 'Full SRT import/export, add/edit/delete subtitle items on subtitle tracks', icon: Subtitles },
                            { title: 'Gallery Stills', desc: 'Grab stills, list gallery, apply grades from stills for versioning', icon: Palette },
                            { title: 'EQ & Sends', desc: '6-band parametric EQ, track sends to buses, bus configuration, automation', icon: Music2 },
                            { title: 'CLI Scripting', desc: 'Run arbitrary Resolve Python scripts with pre-initialized globals', icon: Terminal },
                            { title: 'Render CLI', desc: 'Direct timeline rendering with format/codec/resolution options', icon: MonitorPlay },
                            { title: 'Import CLI', desc: 'Bulk media import with folder targeting from command line', icon: Upload },
                        ].map(({ title, desc, icon: Icon }) => (
                            <div key={title} className="p-4 rounded-lg border border-slate-800 bg-slate-950/30">
                                <Icon className="h-5 w-5 text-blue-400 mb-2" />
                                <h4 className="text-sm font-medium text-white mb-1">{title}</h4>
                                <p className="text-xs text-slate-400">{desc}</p>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
