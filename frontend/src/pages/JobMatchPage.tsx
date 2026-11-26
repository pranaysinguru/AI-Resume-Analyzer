import React, { useEffect, useState } from "react";
import { BookOpen, CheckCircle2, ExternalLink, Loader2, Sparkles, Target, XCircle } from "lucide-react";
import { api } from "../api/client";
import type { JobMatchResult, ResumeDetail, SkillGapResult } from "../types/api";
import { ScoreGauge } from "../components/ScoreGauge";

interface JobMatchPageProps {
  resume: ResumeDetail | null;
  onOpenUpload: () => void;
  onMatchSaved: () => void;
}

export const JobMatchPage: React.FC<JobMatchPageProps> = ({
  resume,
  onOpenUpload,
  onMatchSaved,
}) => {
  const [jobTitle, setJobTitle] = useState("Applied AI / Full Stack Engineer");
  const [company, setCompany] = useState("");
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [matchResult, setMatchResult] = useState<JobMatchResult | null>(null);
  const [skillGaps, setSkillGaps] = useState<SkillGapResult | null>(null);
  const [history, setHistory] = useState<
    {
      id: number;
      job_title: string;
      company: string | null;
      overall_score: number;
      skill_coverage: number;
      semantic_similarity: number;
      created_at: string;
    }[]
  >([]);

  useEffect(() => {
    if (!resume) return;
    api.getMatchHistory(resume.id).then(setHistory).catch(() => {});
  }, [resume?.id]);

  if (!resume) {
    return (
      <div className="gradient-border-card p-10 text-center max-w-2xl mx-auto mt-10">
        <Target className="w-10 h-10 text-indigo-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Upload a Resume to Match Jobs</h2>
        <p className="text-sm text-slate-500 mt-1">
          Compare your resume against any job description using Sentence Transformers and generate a prioritized skill-gap roadmap.
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

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (jd.trim().length < 30) {
      setError("Please paste at least 30 characters of a job description.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [matchRes, gapRes] = await Promise.all([
        api.runJobMatch({
          resume_version_id: resume.id,
          job_title: jobTitle.trim() || "Target Role",
          company: company.trim() || undefined,
          job_description: jd,
        }),
        api.analyzeSkillGaps({
          resume_version_id: resume.id,
          target_role: jobTitle.trim() || undefined,
          job_description: jd,
        }),
      ]);
      setMatchResult(matchRes);
      setSkillGaps(gapRes);
      const updatedHistory = await api.getMatchHistory(resume.id);
      setHistory(updatedHistory);
      onMatchSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Job matching failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          AI Job Matching & Skill Gap Intelligence
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Hybrid bi-encoder semantic similarity, skill evidence coverage, and personalized learning roadmaps.
        </p>
      </div>

      <form onSubmit={handleAnalyze} className="gradient-border-card p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">
              Target Job Title
            </label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">
              Company (optional)
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g., Anthropic, Stripe, Google"
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">
            Paste Job Description
          </label>
          <textarea
            rows={6}
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste full job responsibilities, required tech stack, qualifications, and experience expectations..."
            className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 p-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {error && <p className="text-xs text-rose-500">{error}</p>}

        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-slate-500">
            Matching against <span className="font-semibold text-indigo-500">{resume.version_label}</span>
          </p>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold disabled:opacity-60"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? "Computing Semantic Similarity..." : "Run Semantic Match & Skill Roadmap"}
          </button>
        </div>
      </form>

      {matchResult && (
        <div className="space-y-6">
          {/* Score Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="gradient-border-card p-6 flex flex-col items-center justify-center">
              <ScoreGauge
                score={matchResult.overall_match_score}
                label={matchResult.compatibility_band}
                sublabel={matchResult.job_title}
                size={156}
              />
              <div className="w-full mt-5 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Skill Coverage (44%)</span>
                  <span className="font-bold">{matchResult.score_breakdown.skill_coverage.score}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Semantic Similarity (41%)</span>
                  <span className="font-bold">{matchResult.score_breakdown.semantic_similarity.score}%</span>
                </div>
                <div className="flex justify-between text-[11px] text-slate-400 pl-3">
                  <span>Bi-Encoder / TF-IDF</span>
                  <span>
                    {matchResult.score_breakdown.semantic_similarity.dense_biencoder_score}% /{" "}
                    {matchResult.score_breakdown.semantic_similarity.tfidf_lexical_score}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Experience Alignment (15%)</span>
                  <span className="font-bold">{matchResult.score_breakdown.experience_alignment.score}%</span>
                </div>
              </div>
            </div>

            <div className="gradient-border-card p-6 lg:col-span-2 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-bold text-emerald-500 flex items-center gap-1.5 mb-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Matched Skills ({matchResult.matched_skills.length})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {matchResult.evidenced_matched_skills.map((s) => (
                      <span key={s} className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-400">
                        ✓ {s} (proven)
                      </span>
                    ))}
                    {matchResult.declared_only_matched_skills.map((s) => (
                      <span key={s} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-cyan-500/15 text-cyan-400">
                        {s} (listed)
                      </span>
                    ))}
                    {matchResult.matched_skills.length === 0 && (
                      <span className="text-xs text-slate-500">No direct catalog skills matched.</span>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-rose-500 flex items-center gap-1.5 mb-2">
                    <XCircle className="w-4 h-4" />
                    Missing Skills ({matchResult.missing_skills.length})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {matchResult.missing_skills.map((s) => (
                      <span key={s} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-rose-500/15 text-rose-400">
                        + {s}
                      </span>
                    ))}
                    {matchResult.missing_skills.length === 0 && (
                      <span className="text-xs text-emerald-500">All detected JD skills covered!</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Requirement-to-Resume Evidence Alignment
                </h4>
                <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                  {matchResult.requirement_alignments.map((req, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-100 dark:bg-navy-950 text-xs">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="font-semibold text-slate-800 dark:text-slate-100">
                          JD: {req.requirement}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] shrink-0 ${
                            req.status === "strong"
                              ? "bg-emerald-500/20 text-emerald-400"
                              : req.status === "partial"
                              ? "bg-amber-500/20 text-amber-400"
                              : "bg-rose-500/20 text-rose-400"
                          }`}
                        >
                          {req.similarity_score}% ({req.status})
                        </span>
                      </div>
                      <p className="text-slate-500 dark:text-slate-400">
                        Closest resume evidence: "{req.best_resume_evidence}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Personalized Learning Roadmap */}
          {skillGaps && (
            <div className="gradient-border-card p-6 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="text-lg font-bold flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-cyan-500" />
                    Personalized Skill Gap Learning Roadmap
                  </h3>
                  <p className="text-xs text-slate-500">
                    Context: {skillGaps.target_role_context} • Est. {skillGaps.estimated_total_hours} focused study/build hours
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {skillGaps.roadmap.map((phase) => (
                  <div
                    key={phase.phase}
                    className="p-4 rounded-xl bg-slate-100/80 dark:bg-navy-950/80 border border-slate-200 dark:border-slate-800 space-y-3"
                  >
                    <div>
                      <h4 className="font-bold text-sm text-indigo-500">{phase.phase}</h4>
                      <p className="text-xs text-slate-500 mt-0.5">{phase.goal}</p>
                    </div>
                    {phase.items.length === 0 ? (
                      <p className="text-xs text-emerald-500">No gaps in this tier.</p>
                    ) : (
                      <div className="space-y-2.5">
                        {phase.items.map((item) => (
                          <div key={item.skill} className="p-3 rounded-lg bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 text-xs space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="font-bold">{item.skill}</span>
                              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-400">
                                {item.priority} • {item.hours}h
                              </span>
                            </div>
                            <p className="text-slate-500">{item.project}</p>
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-cyan-500 hover:underline font-medium"
                            >
                              {item.resource}
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="gradient-border-card p-5">
          <h3 className="font-bold text-sm mb-3">Saved Job Match History</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {history.slice(0, 6).map((h) => (
              <div key={h.id} className="p-3.5 rounded-xl bg-slate-100 dark:bg-navy-950 text-xs flex items-center justify-between">
                <div>
                  <p className="font-bold">{h.job_title}</p>
                  <p className="text-slate-500">{h.company || "Target Company"}</p>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-indigo-500/15 text-indigo-500 font-bold">
                  {h.overall_score}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
