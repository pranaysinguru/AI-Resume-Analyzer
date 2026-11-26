import React from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  Award,
  BrainCircuit,
  Briefcase,
  CheckCircle2,
  MessageSquare,
  TrendingUp,
  Upload,
} from "lucide-react";
import type { DashboardOverview } from "../types/api";
import { ScoreGauge } from "../components/ScoreGauge";

interface DashboardPageProps {
  data: DashboardOverview | null;
  loading: boolean;
  onOpenUpload: () => void;
  onNavigate: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  data,
  loading,
  onOpenUpload,
  onNavigate,
}) => {
  if (loading && !data) {
    return (
      <div className="p-8 text-center text-slate-500">
        Loading Career Intelligence Dashboard...
      </div>
    );
  }

  if (!data || !data.has_data || !data.active_resume) {
    return (
      <div className="max-w-3xl mx-auto mt-10 gradient-border-card p-10 text-center">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center mb-4">
          <BrainCircuit className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-bold">No Resumes Analyzed Yet</h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
          Upload your first PDF or DOCX resume to compute live ATS scores, synthesize your Career Twin, and unlock AI job matching. All dashboard metrics reflect real persisted analyses.
        </p>
        <button
          onClick={onOpenUpload}
          className="mt-6 inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-glow transition-all"
        >
          <Upload className="w-4 h-4" />
          Upload Resume to Start
        </button>
      </div>
    );
  }

  const m = data.summary_metrics;
  const active = data.active_resume;

  const kpis = [
    {
      label: "Active ATS Score",
      value: `${m.latest_ats_score.toFixed(1)}`,
      sub: `Grade ${active.quality_grade} • Best: ${m.best_ats_score.toFixed(1)}`,
      icon: Award,
      color: "text-cyan-500 bg-cyan-500/10",
    },
    {
      label: "Career Twin Health",
      value: `${m.career_twin_health.toFixed(1)}%`,
      sub: `${active.evidenced_skills_count}/${active.technical_skills_count} skills verified`,
      icon: BrainCircuit,
      color: "text-indigo-500 bg-indigo-500/10",
    },
    {
      label: "Job Matches Run",
      value: `${m.total_job_matches}`,
      sub:
        m.total_job_matches > 0
          ? `Avg match: ${m.avg_job_match_score.toFixed(1)}%`
          : "Run your first JD match",
      icon: Briefcase,
      color: "text-violet-500 bg-violet-500/10",
    },
    {
      label: "Interview Prep Packs",
      value: `${m.interview_sessions_count}`,
      sub: `${m.total_versions} resume version(s) stored`,
      icon: MessageSquare,
      color: "text-emerald-500 bg-emerald-500/10",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Career Intelligence Dashboard
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Active Snapshot: <span className="font-semibold text-indigo-500">{active.version_label}</span> ({active.filename})
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onNavigate("job-match")}
            className="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 text-sm font-medium hover:border-indigo-500 transition-colors"
          >
            Match a Job Description
          </button>
          <button
            onClick={onOpenUpload}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-colors"
          >
            <Upload className="w-4 h-4" />
            New Version
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="gradient-border-card p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  {kpi.label}
                </span>
                <div className={`p-2 rounded-lg ${kpi.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-3xl font-extrabold tracking-tight">{kpi.value}</div>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{kpi.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="gradient-border-card p-5 flex flex-col items-center justify-center">
          <ScoreGauge
            score={active.ats_score}
            label="Overall ATS Compatibility"
            sublabel={`Grade ${active.quality_grade}`}
            size={156}
          />
          <div className="w-full mt-5 space-y-2.5">
            {active.ats_dimensions.map((dim) => (
              <div key={dim.key}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-600 dark:text-slate-300 truncate pr-2">
                    {dim.label}
                  </span>
                  <span className="font-mono font-semibold">{dim.score.toFixed(0)}%</span>
                </div>
                <div className="h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400"
                    style={{ width: `${dim.score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="gradient-border-card p-5 lg:col-span-2 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-indigo-500" />
                Resume ATS Trajectory
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Score progression across uploaded resume versions
              </p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.ats_trend}>
                <defs>
                  <linearGradient id="atsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.25} />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="ats_score"
                  name="ATS Score"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fill="url(#atsGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row: Skill Distribution + Career Predictions + Action Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="gradient-border-card p-5">
          <h3 className="font-bold text-base flex items-center gap-2 mb-1">
            <Activity className="w-4 h-4 text-cyan-500" />
            Skill Distribution (Total vs. Project/Work Evidenced)
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
            Compares skills listed anywhere on your resume vs. skills backed by experience/projects
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.skill_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.25} />
                <XAxis dataKey="category" tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="total" name="Total Skills" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="evidenced" name="Evidenced" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="gradient-border-card p-5 flex flex-col justify-between space-y-4">
          <div>
            <h3 className="font-bold text-base mb-3">Top Recommended Roles & Next Actions</h3>
            <div className="space-y-2.5">
              {data.top_career_recommendations.slice(0, 3).map((rec) => (
                <div
                  key={rec.role}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-100/80 dark:bg-navy-950/70 border border-slate-200 dark:border-slate-800"
                >
                  <div>
                    <p className="text-sm font-semibold">{rec.role}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {rec.matched_core_skills.slice(0, 4).join(", ")}
                    </p>
                  </div>
                  <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-500/15 text-indigo-500">
                    {rec.fit_score}% fit
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Highest-Uplift Resume Fixes
            </h4>
            <ul className="space-y-1.5">
              {data.priority_recommendations.slice(0, 3).map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mt-0.5 shrink-0" />
                  <span>{item.recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
