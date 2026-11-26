import React, { useEffect, useState } from "react";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { BrainCircuit, Compass, Loader2, RefreshCw, ShieldCheck } from "lucide-react";
import { api } from "../api/client";
import type { CareerTwinData, ResumeDetail } from "../types/api";
import { ScoreGauge } from "../components/ScoreGauge";

interface CareerTwinPageProps {
  resume: ResumeDetail | null;
  onOpenUpload: () => void;
}

export const CareerTwinPage: React.FC<CareerTwinPageProps> = ({ resume, onOpenUpload }) => {
  const [twin, setTwin] = useState<CareerTwinData | null>(null);
  const [interestsInput, setInterestsInput] = useState("AI, Backend, Distributed Systems");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!resume) return;
    setLoading(true);
    api
      .getLatestTwin(resume.id)
      .then(setTwin)
      .finally(() => setLoading(false));
  }, [resume?.id]);

  if (!resume) {
    return (
      <div className="gradient-border-card p-10 text-center max-w-2xl mx-auto mt-10">
        <BrainCircuit className="w-10 h-10 text-indigo-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Synthesize Your Digital Career Twin</h2>
        <p className="text-sm text-slate-500 mt-1">
          Upload a resume to build an evidence-backed Career Twin mapping proven skills, career role predictions, and a 30-60-90 day plan.
        </p>
        <button
          onClick={onOpenUpload}
          className="mt-5 px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold"
        >
          Upload Resume
        </button>
      </div>
    );
  }

  const handleResynthesize = async () => {
    setLoading(true);
    try {
      const interests = interestsInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const updated = await api.synthesizeTwin({
        resume_version_id: resume.id,
        career_interests: interests,
      });
      setTwin(updated);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !twin) {
    return <div className="p-8 text-center text-slate-500">Synthesizing Career Twin...</div>;
  }

  if (!twin) return null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-indigo-500" />
            Intelligent Career Twin
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Evidence-backed digital profile powering role prediction, skill gap intelligence, and 90-day planning.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <input
            type="text"
            value={interestsInput}
            onChange={(e) => setInterestsInput(e.target.value)}
            placeholder="Career interests (comma-separated)"
            className="rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-900 px-3 py-2 text-xs w-64 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={handleResynthesize}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
            Update Twin
          </button>
        </div>
      </div>

      {/* Top Identity & Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="gradient-border-card p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-500">
                Digital Twin Identity
              </span>
              <h2 className="text-xl font-extrabold mt-1">{twin.identity.candidate_label}</h2>
              <p className="text-xs text-slate-500">{twin.identity.inferred_seniority}</p>
            </div>
            <ScoreGauge score={twin.twin_health_score} label="Twin Health" size={110} />
          </div>

          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Top Role Match</span>
              <span className="font-bold text-cyan-500">{twin.identity.primary_recommended_role}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Verified Skills</span>
              <span className="font-semibold">{twin.skill_graph.verified_skills.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Declared-Only Skills</span>
              <span className="font-semibold text-amber-500">{twin.skill_graph.declared_only_skills.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Quantified Bullets</span>
              <span className="font-semibold">
                {twin.evidence_pillars.quantified_achievements_count} / {twin.evidence_pillars.total_bullets_count}
              </span>
            </div>
          </div>
        </div>

        <div className="gradient-border-card p-5 lg:col-span-2">
          <h3 className="font-bold text-base mb-1">Career Readiness Radar</h3>
          <p className="text-xs text-slate-500 mb-2">
            Multi-dimensional readiness across ATS parsing, project evidence, role fit, and metrics
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={twin.readiness_radar}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Radar
                  name="Readiness"
                  dataKey="score"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.35}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Career Predictions with Reasoning */}
      <div className="gradient-border-card p-6 space-y-4">
        <h3 className="font-bold text-base flex items-center gap-2">
          <Compass className="w-5 h-5 text-cyan-500" />
          Explainable Career Predictions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {twin.career_predictions.map((pred) => (
            <div
              key={pred.role}
              className="p-4 rounded-xl bg-slate-100/80 dark:bg-navy-950/80 border border-slate-200 dark:border-slate-800 space-y-2.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="font-bold text-sm">{pred.role}</h4>
                  <p className="text-xs text-slate-500">{pred.summary}</p>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-indigo-500/15 text-indigo-500 font-bold text-xs shrink-0">
                  {pred.fit_score}% ({pred.confidence})
                </span>
              </div>
              <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-300">
                {pred.reasoning.map((r, i) => (
                  <li key={i}>• {r}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Skill Evidence Graph + 30-60-90 Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="gradient-border-card p-6 space-y-4">
          <h3 className="font-bold text-base flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            Skill Evidence Graph
          </h3>
          <div>
            <p className="text-xs font-semibold text-emerald-500 mb-2">
              Evidence-Backed Skills (Proven in Experience / Projects)
            </p>
            <div className="flex flex-wrap gap-1.5">
              {twin.skill_graph.verified_skills.map((s) => (
                <span key={s.skill} className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-400">
                  {s.skill} • {s.mentions}x
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-amber-500 mb-2">
              Declared-Only Skills (Add Project Proof to Strengthen Twin)
            </p>
            <div className="flex flex-wrap gap-1.5">
              {twin.skill_graph.declared_only_skills.map((s) => (
                <span key={s.skill} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/15 text-amber-400">
                  {s.skill}
                </span>
              ))}
              {twin.skill_graph.declared_only_skills.length === 0 && (
                <span className="text-xs text-emerald-500">All declared skills have project or work proof!</span>
              )}
            </div>
          </div>
        </div>

        <div className="gradient-border-card p-6 space-y-3">
          <h3 className="font-bold text-base">30-60-90 Day Career Twin Plan</h3>
          {twin.action_plan_30_60_90.map((step) => (
            <div key={step.horizon} className="p-3.5 rounded-xl bg-slate-100 dark:bg-navy-950 text-xs space-y-1">
              <p className="font-bold text-indigo-500">{step.horizon}</p>
              <p className="text-slate-500">{step.focus}</p>
              <ul className="space-y-1 pt-1 text-slate-700 dark:text-slate-300">
                {step.actions.map((act, i) => (
                  <li key={i}>→ {act}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
