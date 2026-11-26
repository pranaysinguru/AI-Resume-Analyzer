import React, { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowRight, GitCompare, Loader2, Upload } from "lucide-react";
import { api } from "../api/client";
import type { ResumeSummary, VersionCompareResponse } from "../types/api";

interface VersionsPageProps {
  resumes: ResumeSummary[];
  onOpenUpload: () => void;
}

export const VersionsPage: React.FC<VersionsPageProps> = ({ resumes, onOpenUpload }) => {
  const [baseId, setBaseId] = useState<string>(resumes[1]?.id ? String(resumes[1].id) : "");
  const [targetId, setTargetId] = useState<string>(resumes[0]?.id ? String(resumes[0].id) : "");
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [diff, setDiff] = useState<VersionCompareResponse | null>(null);

  if (resumes.length < 2) {
    return (
      <div className="gradient-border-card p-10 text-center max-w-2xl mx-auto mt-10">
        <GitCompare className="w-10 h-10 text-indigo-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Upload At Least Two Resume Versions</h2>
        <p className="text-sm text-slate-500 mt-1">
          Version Intelligence tracks ATS score improvements, newly evidenced skills, bullet upgrades, and job compatibility gains across iterations.
        </p>
        <button
          onClick={onOpenUpload}
          className="mt-5 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold"
        >
          <Upload className="w-4 h-4" />
          Upload Another Version
        </button>
      </div>
    );
  }

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!baseId || !targetId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareVersions({
        base_version_id: Number(baseId),
        target_version_id: Number(targetId),
        job_description: jd.trim() || undefined,
      });
      setDiff(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Resume Version Intelligence</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Compare two resume iterations to quantify ATS gains, skill evidence growth, and job match improvement.
        </p>
      </div>

      <form onSubmit={handleCompare} className="gradient-border-card p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">
              Base Version (Before)
            </label>
            <select
              value={baseId}
              onChange={(e) => setBaseId(e.target.value)}
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3.5 py-2.5 text-sm"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.version_label} (ATS {r.ats_score})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">
              Target Version (After)
            </label>
            <select
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3.5 py-2.5 text-sm"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.version_label} (ATS {r.ats_score})
                </option>
              ))}
            </select>
          </div>
        </div>

        <textarea
          rows={3}
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder="Optional: Paste a Job Description to measure how much compatibility improved between versions..."
          className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 p-3 text-sm"
        />

        {error && <p className="text-xs text-rose-500">{error}</p>}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !baseId || !targetId}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <GitCompare className="w-4 h-4" />}
            Compare Versions
          </button>
        </div>
      </form>

      {diff && (
        <div className="space-y-5">
          <div className="gradient-border-card p-6 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div>
                <p className="text-xs text-slate-500">Base</p>
                <p className="font-bold">{diff.base_version.version_label}</p>
                <p className="text-lg font-extrabold">{diff.base_version.ats_score}</p>
              </div>
              <ArrowRight className="w-5 h-5 text-indigo-500" />
              <div>
                <p className="text-xs text-slate-500">Target</p>
                <p className="font-bold">{diff.target_version.version_label}</p>
                <p className="text-lg font-extrabold text-cyan-500">{diff.target_version.ats_score}</p>
              </div>
            </div>

            <div className="text-right">
              <span
                className={`inline-block px-3 py-1 rounded-xl text-sm font-extrabold ${
                  diff.ats_score_delta >= 0
                    ? "bg-emerald-500/15 text-emerald-500"
                    : "bg-rose-500/15 text-rose-500"
                }`}
              >
                {diff.ats_score_delta >= 0 ? `+${diff.ats_score_delta}` : diff.ats_score_delta} ATS pts
              </span>
              <p className="text-xs text-slate-500 mt-1">{diff.summary}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="gradient-border-card p-5">
              <h3 className="font-bold text-base mb-3">ATS Dimension Comparison</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={diff.dimension_deltas}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.25} />
                    <XAxis dataKey="key" tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="base_score" name="Base" fill="#64748b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="target_score" name="Target" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="gradient-border-card p-5 space-y-4 text-xs">
              <h3 className="font-bold text-base">Skills & Bullet Quality Deltas</h3>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-navy-950">
                  <p className="text-lg font-bold text-cyan-500">
                    {diff.bullet_quality_delta.quantified_bullets_delta >= 0 ? "+" : ""}
                    {diff.bullet_quality_delta.quantified_bullets_delta}
                  </p>
                  <p className="text-slate-500">Quantified Bullets</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-navy-950">
                  <p className="text-lg font-bold text-indigo-500">
                    {diff.bullet_quality_delta.strong_verb_delta >= 0 ? "+" : ""}
                    {diff.bullet_quality_delta.strong_verb_delta}
                  </p>
                  <p className="text-slate-500">Strong Verbs</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-100 dark:bg-navy-950">
                  <p className="text-lg font-bold text-emerald-500">
                    +{diff.skills_diff.newly_evidenced.length}
                  </p>
                  <p className="text-slate-500">Newly Evidenced</p>
                </div>
              </div>

              {diff.skills_diff.added.length > 0 && (
                <div>
                  <p className="font-semibold text-emerald-500 mb-1">Added Skills</p>
                  <p className="text-slate-600 dark:text-slate-300">{diff.skills_diff.added.join(", ")}</p>
                </div>
              )}

              {diff.job_compatibility_delta && (
                <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/25">
                  <p className="font-bold text-indigo-400">
                    Job Compatibility Delta: {diff.job_compatibility_delta.base_match_score}% →{" "}
                    {diff.job_compatibility_delta.target_match_score}% (
                    {diff.job_compatibility_delta.delta >= 0 ? "+" : ""}
                    {diff.job_compatibility_delta.delta}%)
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
