import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  Eye,
  FileSearch,
  ShieldAlert,
  Sparkles,
  Wand2,
} from "lucide-react";
import { api } from "../api/client";
import type { BulletEnhancementResponse, ResumeDetail } from "../types/api";
import { ScoreGauge } from "../components/ScoreGauge";

interface AnalyzerPageProps {
  resume: ResumeDetail | null;
  onOpenUpload: () => void;
}

export const AnalyzerPage: React.FC<AnalyzerPageProps> = ({ resume, onOpenUpload }) => {
  const [subTab, setSubTab] = useState<"overview" | "ats" | "recruiter" | "enhancer">("overview");
  const [customBullets, setCustomBullets] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [enhanced, setEnhanced] = useState<BulletEnhancementResponse | null>(null);
  const [enhancing, setEnhancing] = useState(false);
  const [enhanceError, setEnhanceError] = useState<string | null>(null);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  if (!resume) {
    return (
      <div className="gradient-border-card p-10 text-center max-w-2xl mx-auto mt-10">
        <FileSearch className="w-10 h-10 text-indigo-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Select or Upload a Resume</h2>
        <p className="text-sm text-slate-500 mt-1">
          Inspect extracted structure, ATS subscores, recruiter red flags, and zero-fabrication bullet rewrites.
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

  const parsed = resume.parsed_data;
  const ats = resume.ats_report;
  const recruiter = resume.recruiter_audit;

  const handleRunEnhance = async (useCustom: boolean) => {
    setEnhancing(true);
    setEnhanceError(null);
    try {
      const bullets = useCustom
        ? customBullets
            .split("\n")
            .map((l) => l.trim())
            .filter(Boolean)
        : [];
      const res = await api.enhanceBullets({
        resume_version_id: useCustom ? undefined : resume.id,
        bullets,
        target_role: targetRole.trim() || undefined,
      });
      setEnhanced(res);
    } catch (err) {
      setEnhanceError(err instanceof Error ? err.message : "Enhancement failed.");
    } finally {
      setEnhancing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Resume Intelligence Studio</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {resume.version_label} • {resume.word_count} words • {resume.page_count} page(s) • PII Masked
          </p>
        </div>

        <div className="flex flex-wrap gap-1.5 p-1 rounded-xl bg-slate-200/70 dark:bg-navy-900 border border-slate-300/60 dark:border-slate-800">
          {[
            { id: "overview", label: "Parsed Intelligence", icon: FileSearch },
            { id: "ats", label: "ATS Simulator", icon: CheckCircle2 },
            { id: "recruiter", label: "Recruiter Mode", icon: Eye },
            { id: "enhancer", label: "Bullet Enhancer", icon: Sparkles },
          ].map((t) => {
            const Icon = t.icon;
            const active = subTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setSubTab(t.id as typeof subTab)}
                className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  active
                    ? "bg-indigo-600 text-white shadow"
                    : "text-slate-600 dark:text-slate-300 hover:bg-white/60 dark:hover:bg-navy-800"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {t.label}
              </button>
            );
          })}
        </div>
      </div>

      {subTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="gradient-border-card p-5 space-y-4">
            <h3 className="font-bold text-base">Candidate & Privacy Check</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500">Identifier</span>
                <span className="font-semibold">{parsed.contact.candidate_label}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500">Email (Masked)</span>
                <span className="font-mono">{parsed.contact.email_masked ?? "Missing"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500">Phone (Masked)</span>
                <span className="font-mono">{parsed.contact.phone_masked ?? "Missing"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500">Experience Est.</span>
                <span className="font-semibold">{parsed.estimated_years_experience} yrs</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Multi-Column Risk</span>
                <span className={parsed.layout.multi_column_risk ? "text-amber-500 font-semibold" : "text-emerald-500 font-semibold"}>
                  {parsed.layout.multi_column_risk ? "Detected" : "Clean Single-Flow"}
                </span>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Sections Found
              </p>
              <div className="flex flex-wrap gap-1.5">
                {parsed.sections_present.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-500 capitalize">
                    {s}
                  </span>
                ))}
                {parsed.missing_sections.map((s) => (
                  <span key={s} className="px-2.5 py-1 rounded-md text-xs font-medium bg-rose-500/10 text-rose-400 capitalize">
                    Missing: {s}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="gradient-border-card p-5 lg:col-span-2 space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                <h4 className="text-sm font-bold text-emerald-500 mb-2">Identified Strengths</h4>
                <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-300">
                  {parsed.diagnostics.strengths.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
              <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                <h4 className="text-sm font-bold text-amber-500 mb-2">Weaknesses & Missing Signals</h4>
                <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-300">
                  {parsed.diagnostics.weaknesses.map((w, i) => (
                    <li key={i}>• {w}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-bold mb-2">
                Extracted Skills ({parsed.skills.evidenced_skills.length} Verified in Projects/Work, {parsed.skills.unverified_skills.length} Declared-Only)
              </h4>
              <div className="flex flex-wrap gap-2">
                {parsed.skills.evidenced_skills.map((skill) => (
                  <span
                    key={skill}
                    title="Backed by Experience or Project bullets"
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-cyan-500/15 text-cyan-400 border border-cyan-500/25"
                  >
                    ✓ {skill}
                  </span>
                ))}
                {parsed.skills.unverified_skills.map((skill) => (
                  <span
                    key={skill}
                    title="Listed in Skills section without project/work evidence"
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Experience Entries ({parsed.experience_entries.length})
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {parsed.experience_entries.map((e, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-slate-100 dark:bg-navy-950 text-xs">
                      <p className="font-semibold">{e.title_line}</p>
                      <p className="text-slate-500 mt-0.5">{e.highlights.length} highlight(s)</p>
                    </div>
                  ))}
                  {parsed.experience_entries.length === 0 && (
                    <p className="text-xs text-slate-500">No work experience section detected.</p>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Project Entries ({parsed.project_entries.length})
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {parsed.project_entries.map((p, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-slate-100 dark:bg-navy-950 text-xs">
                      <p className="font-semibold">{p.title_line}</p>
                      <p className="text-slate-500 mt-0.5">{p.highlights.length} highlight(s)</p>
                    </div>
                  ))}
                  {parsed.project_entries.length === 0 && (
                    <p className="text-xs text-slate-500">No projects section detected.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {subTab === "ats" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="gradient-border-card p-6 flex flex-col items-center">
            <ScoreGauge
              score={ats.overall_score}
              label={`Grade ${ats.grade}`}
              sublabel={ats.pass_likelihood}
              size={165}
            />
            <div className="w-full mt-6 pt-5 border-t border-slate-200 dark:border-slate-800 space-y-2.5">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Prioritized Uplift Actions
              </h4>
              {ats.action_plan.map((item, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-100 dark:bg-navy-950 text-xs">
                  <div className="flex justify-between font-semibold mb-1">
                    <span className="text-indigo-500">{item.dimension}</span>
                    <span className="text-emerald-500">+{item.estimated_score_uplift} pts est.</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300">{item.recommendation}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-2 space-y-4">
            {ats.dimensions.map((dim) => (
              <div key={dim.key} className="gradient-border-card p-5">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div>
                    <h4 className="font-bold text-base">{dim.label}</h4>
                    <p className="text-xs text-slate-500">
                      Weight: {(dim.weight * 100).toFixed(0)}% • Contribution: {dim.weighted_points} pts
                    </p>
                  </div>
                  <span className="text-xl font-extrabold text-indigo-500">
                    {dim.score.toFixed(1)}/100
                  </span>
                </div>
                <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-800 mb-3 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400"
                    style={{ width: `${dim.score}%` }}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div>
                    <p className="font-semibold text-slate-500 mb-1">Explainable Evidence</p>
                    <ul className="space-y-1 text-slate-600 dark:text-slate-300">
                      {dim.evidence.map((ev, i) => (
                        <li key={i}>✓ {ev}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-500 mb-1">Actionable Recommendations</p>
                    {dim.recommendations.length > 0 ? (
                      <ul className="space-y-1 text-amber-600 dark:text-amber-300">
                        {dim.recommendations.map((rec, i) => (
                          <li key={i}>→ {rec}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-emerald-500">No critical issues in this dimension.</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {subTab === "recruiter" && (
        <div className="space-y-5">
          <div className="gradient-border-card p-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-500">
                Recruiter Perspective Audit
              </span>
              <h2 className="text-2xl font-extrabold mt-1">{recruiter.hiring_manager_verdict}</h2>
              <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">
                {recruiter.verdict_reasoning}
              </p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-navy-950">
                <p className="text-lg font-bold">{recruiter.seven_second_scan.inferred_experience_years}y</p>
                <p className="text-[11px] text-slate-500">Experience</p>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-navy-950">
                <p className="text-lg font-bold">{recruiter.seven_second_scan.projects_detected}</p>
                <p className="text-[11px] text-slate-500">Projects</p>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-navy-950">
                <p className="text-lg font-bold">{recruiter.seven_second_scan.top_evidenced_skills.length}</p>
                <p className="text-[11px] text-slate-500">Top Proven</p>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-navy-950">
                <p className="text-lg font-bold">{recruiter.red_flags.length}</p>
                <p className="text-[11px] text-slate-500">Red Flags</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="gradient-border-card p-5 space-y-3">
              <h3 className="font-bold text-base flex items-center gap-2 text-rose-500">
                <ShieldAlert className="w-4 h-4" />
                Critical Hiring Manager Red Flags
              </h3>
              {recruiter.red_flags.length === 0 ? (
                <p className="text-sm text-emerald-500">No major red flags detected during recruiter scan.</p>
              ) : (
                recruiter.red_flags.map((rf, i) => (
                  <div key={i} className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/20 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm">{rf.category}</span>
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase bg-rose-500/20 text-rose-400">
                        {rf.severity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300">{rf.detail}</p>
                    <p className="text-xs text-indigo-500 font-medium">Fix: {rf.fix}</p>
                  </div>
                ))
              )}
            </div>

            <div className="gradient-border-card p-5 space-y-3">
              <h3 className="font-bold text-base flex items-center gap-2 text-amber-500">
                <AlertTriangle className="w-4 h-4" />
                Bullets Needing Evidence or Metrics
              </h3>
              {recruiter.unclear_bullets.length === 0 ? (
                <p className="text-sm text-emerald-500">All detected bullets demonstrate clear ownership and metrics.</p>
              ) : (
                recruiter.unclear_bullets.map((b, i) => (
                  <div key={i} className="p-3.5 rounded-xl bg-slate-100 dark:bg-navy-950 text-xs space-y-1">
                    <p className="font-medium text-slate-800 dark:text-slate-200">"{b.original}"</p>
                    <p className="text-amber-500 font-semibold">Audit note: {b.reason}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {subTab === "enhancer" && (
        <div className="space-y-5">
          <div className="gradient-border-card p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-bold text-base">Zero-Fabrication AI Bullet Enhancer</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Strengthens action verbs and executive clarity without inventing numbers or fake skills.
                </p>
              </div>
              <button
                onClick={() => handleRunEnhance(false)}
                disabled={enhancing}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
              >
                <Wand2 className="w-3.5 h-3.5" />
                {enhancing ? "Enhancing..." : "Auto-Enhance Weak Resume Bullets"}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <textarea
                rows={4}
                value={customBullets}
                onChange={(e) => setCustomBullets(e.target.value)}
                placeholder="Or paste custom bullet points here (one per line)..."
                className="md:col-span-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <div className="flex flex-col justify-between gap-2">
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="Optional target role (e.g., ML Engineer)"
                  className="rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={() => handleRunEnhance(true)}
                  disabled={enhancing || !customBullets.trim()}
                  className="w-full py-2.5 rounded-xl border border-indigo-500/40 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-500 font-semibold text-xs disabled:opacity-50"
                >
                  Enhance Pasted Bullets
                </button>
              </div>
            </div>
            {enhanceError && <p className="text-xs text-rose-500">{enhanceError}</p>}
          </div>

          {enhanced && (
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-600 dark:text-emerald-300">
                {enhanced.policy}
              </div>
              {enhanced.enhancements.map((item, idx) => (
                <div key={idx} className="gradient-border-card p-5 space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="p-3 rounded-xl bg-slate-100 dark:bg-navy-950">
                      <p className="font-semibold text-slate-500 mb-1">Original</p>
                      <p className="text-slate-700 dark:text-slate-300">{item.original}</p>
                    </div>
                    <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/25 relative">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-semibold text-indigo-500">Enhanced (Grounded)</p>
                        <button
                          onClick={() => {
                            navigator.clipboard?.writeText(item.enhanced);
                            setCopiedIdx(idx);
                            setTimeout(() => setCopiedIdx(null), 1500);
                          }}
                          className="inline-flex items-center gap-1 text-[11px] text-indigo-400 hover:underline"
                        >
                          <Copy className="w-3 h-3" />
                          {copiedIdx === idx ? "Copied" : "Copy"}
                        </button>
                      </div>
                      <p className="font-medium text-slate-900 dark:text-white">{item.enhanced}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 text-[11px]">
                    {item.changes_made.map((c, ci) => (
                      <span key={ci} className="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {c}
                      </span>
                    ))}
                  </div>
                  {item.metrics_prompt && (
                    <p className="text-xs text-amber-500">{item.metrics_prompt}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
