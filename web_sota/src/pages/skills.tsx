import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Skill {
  name: string;
  uri: string;
  description: string;
  operations: string[];
}

export function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSkills = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/skills");
      if (!res.ok) throw new Error("Failed to fetch skills");
      const data = await res.json();
      setSkills(data.skills || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  return (
    <div className="space-y-6" data-testid="skills-page">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Skills</h2>
        <p className="text-slate-300">Resolve capability domains exposed to AI assistants</p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-300" data-testid="skills-loading">
          Loading skills...
        </div>
      ) : error ? (
        <div
          className="p-8 text-center border border-slate-800 bg-slate-900/50 rounded-lg text-slate-300"
          data-testid="skills-error"
        >
          <p className="text-red-400 mb-2">Error loading skills</p>
          <p className="text-sm">{error}</p>
          <button
            type="button"
            data-testid="skills-retry"
            onClick={fetchSkills}
            className="mt-4 rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
          >
            Retry
          </button>
        </div>
      ) : skills.length === 0 ? (
        <div className="text-slate-300 italic p-4 border border-slate-800 rounded-md" data-testid="skills-empty">
          No skills registered.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="skills-list">
          {skills.map((skill) => (
            <Card key={skill.name} data-testid="skill-card" className="border-slate-800 bg-slate-950/50">
              <CardHeader>
                <CardTitle className="text-white text-base">{skill.name}</CardTitle>
                <CardDescription className="text-slate-300 font-mono text-sm">{skill.uri}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-300 mb-2">{skill.description}</p>
                <div className="flex flex-wrap gap-1">
                  {skill.operations.map((op) => (
                    <span key={op} className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-sm text-slate-300">
                      {op}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
