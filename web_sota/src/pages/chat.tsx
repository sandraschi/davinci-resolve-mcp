import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, Send, User, Film } from "lucide-react";

export function Chat() {
    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">AI Video Editor</h2>
                    <p className="text-slate-400">Agentic orchestration for professional video workflows</p>
                </div>
            </div>

            <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col mb-4 overflow-hidden">
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/30">
                            <Bot className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="flex-1 space-y-2">
                            <p className="text-sm font-medium text-blue-400">Resolve AI</p>
                            <p className="text-sm text-slate-300 bg-slate-900/50 p-3 rounded-md border border-slate-800">
                                How can I assist with your production today? I can help with:
                            </p>
                            <div className="grid gap-2 text-xs">
                                <span className="text-slate-400 bg-slate-900/30 p-2 rounded border border-slate-800/50">
                                    "Import all .mov files from D:/Footage/ProjectA and create a timeline."
                                </span>
                                <span className="text-slate-400 bg-slate-900/30 p-2 rounded border border-slate-800/50">
                                    "Apply the 'Cinema_Vibe' LUT to all clips in the current timeline."
                                </span>
                                <span className="text-slate-400 bg-slate-900/30 p-2 rounded border border-slate-800/50">
                                    "Setup a 4K ProRes 422 render job for the 'Final Cut' timeline."
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-3 flex-row-reverse">
                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                            <User className="w-5 h-5 text-slate-300" />
                        </div>
                        <div className="flex-1 space-y-2 text-right">
                            <p className="text-sm font-medium text-slate-300">Producer</p>
                            <p className="text-sm text-slate-300 bg-blue-600/10 p-3 rounded-md border border-blue-600/20 inline-block">
                                Optimize the media pool by removing any clips not used in the master timeline.
                            </p>
                        </div>
                    </div>
                </CardContent>

                <div className="p-4 border-t border-slate-800 bg-slate-900/20">
                    <div className="flex gap-2">
                        <Input
                            className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-500"
                            placeholder="Instruct Resolve AI (e.g., 'Perform a ripple cut at 00:12:05')"
                        />
                        <Button className="bg-blue-600 hover:bg-blue-700">
                            <Send className="w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
