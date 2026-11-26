import React, { useState } from "react";
import { ChevronDown, ChevronUp, Loader2, MessageSquareCode, Sparkles } from "lucide-react";
import { api } from "../api/client";
import type { InterviewResponse, ResumeDetail } from "../types/api";

interface InterviewPageProps {
  resume: ResumeDetail | null;
  onOpenUpload: () => void;
  onSessionCreated: () => void;
}

export const InterviewPage: React.FC<InterviewPageProps> = ({
  resume,
  onOpenUpload,
  onSessionCreated,
}) => {
  const [targetRole, setTargetRole] = useState("Full Stack AI Engineer");
  const [difficulty, setDifficulty] = useState<"mixed" | "junior" | "mid" | "senior">("mixed");
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState<InterviewResponse | null>(null);
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [openRubrics, setOpenRubrics] = useState<Record<string, boolean>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});

  if (!resume) {
    return (
      <div className="gradient-border-card p-10 text-center max-w-2xl mx-auto mt-10">
        <MessageSquareCode className="w-10 h-10 text-indigo-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Upload a Resume for AI Interview Prep</h2>
        <p className="text-sm text-slate-500 mt-1">
          Generate tailored technical, project deep-dive, behavioral, and HR questions grounded in your actual resume.
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

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.generateInterview({
        resume_version_id: resume.id,
        target_role: targetRole.trim() || "Software Engineer",
        job_description: jd.trim() || undefined,
        difficulty,
      });
      setSession(res);
      setCategoryFilter("All");
      onSessionCreated();
    } finally {
      setLoading(false);
    }
  };

  const categories = session
    ? ["All", ...Object.keys(session.category_breakdown)]
    : ["All"];
  const visibleQuestions = session
    ? session.questions.filter((q) => categoryFilter === "All" || q.category === categoryFilter)
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">AI Interview Simulator</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Every question is anchored to your real projects, skills, unverified claims, and target job requirements.
        </p>
      </div>

      <form onSubmit={handleGenerate} className="gradient-border-card p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-slate-500 mb-1">Target Role</label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">Difficulty</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as typeof difficulty)}
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="mixed">Mixed (Realistic Loop)</option>
              <option value="junior">Junior / Entry</option>
              <option value="mid">Mid-Level</option>
              <option value="senior">Senior / Lead</option>
            </select>
          </div>
        </div>

        <textarea
          rows={3}
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder="Optional: Paste target job description to probe specific JD skill gaps..."
          className="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-navy-950 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? "Generating Questions..." : "Generate Personalized Interview Pack"}
          </button>
        </div>
      </form>

      {session && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                  categoryFilter === cat
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-200 dark:bg-navy-900 text-slate-600 dark:text-slate-300"
                }`}
              >
                {cat}{" "}
                {cat !== "All" && session.category_breakdown[cat]
                  ? `(${session.category_breakdown[cat]})`
                  : `(${session.total_questions})`}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {visibleQuestions.map((q) => {
              const expanded = Boolean(openRubrics[q.id]);
              return (
                <div key={q.id} className="gradient-border-card p-5 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-md text-xs font-bold bg-indigo-500/15 text-indigo-500">
                        {q.category}
                      </span>
                      <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold uppercase bg-slate-200 dark:bg-slate-800 text-slate-500">
                        {q.difficulty}
                      </span>
                    </div>
                    <span className="text-[11px] text-cyan-500 font-medium">
                      Grounded in: {q.grounded_in.slice(0, 65)}
                    </span>
                  </div>

                  <p className="text-base font-semibold leading-relaxed">{q.question}</p>

                  <textarea
                    rows={2}
                    value={notes[q.id] ?? ""}
                    onChange={(e) => setNotes((prev) => ({ ...prev, [q.id]: e.target.value }))}
                    placeholder="Draft your STAR / technical answer notes here to rehearse..."
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-navy-950 p-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />

                  <button
                    type="button"
                    onClick={() => setOpenRubrics((prev) => ({ ...prev, [q.id]: !expanded }))}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-500 hover:underline"
                  >
                    {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    {expanded ? "Hide Interviewer Rubric" : "Show Interviewer Rubric & Framework"}
                  </button>

                  {expanded && (
                    <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-navy-950 text-xs space-y-2">
                      <p className="font-semibold text-cyan-500">
                        Recommended Structure: {q.answering_framework}
                      </p>
                      <ul className="space-y-1 text-slate-600 dark:text-slate-300">
                        {q.what_interviewers_look_for.map((item, idx) => (
                          <li key={idx}>• {item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
