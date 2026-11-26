import React from "react";
import {
  ArrowRight,
  BrainCircuit,
  Briefcase,
  Cpu,
  Eye,
  GitCompare,
  MessageSquareCode,
  ShieldCheck,
  Sparkles,
  Target,
  Upload,
} from "lucide-react";

interface LandingPageProps {
  onEnterWorkspace: () => void;
  onOpenUpload: () => void;
  hasExistingResumes: boolean;
}

const CAPABILITIES = [
  {
    icon: Cpu,
    title: "Explainable ATS Simulator",
    desc: "Transparent 5-dimension scoring across parser safety, section structure, verified keywords, impact metrics, and readability.",
  },
  {
    icon: Target,
    title: "Semantic AI Job Matching",
    desc: "Hybrid Sentence-Transformer bi-encoder + TF-IDF matching maps every JD requirement to your strongest resume bullet.",
  },
  {
    icon: BrainCircuit,
    title: "Digital Career Twin",
    desc: "Synthesizes an evidence-backed graph separating proven skills from declared-only keywords with a 30-60-90 day roadmap.",
  },
  {
    icon: Eye,
    title: "Recruiter Perspective Mode",
    desc: "Simulates a critical 7-second hiring-manager scan to expose skill inflation, weak phrasing, and missing proof.",
  },
  {
    icon: Sparkles,
    title: "Zero-Fabrication Enhancer",
    desc: "Upgrades weak bullet verbs and clarity while using explicit [metric placeholders]—never inventing fake numbers.",
  },
  {
    icon: MessageSquareCode,
    title: "Grounded Interview Simulator",
    desc: "Generates technical, project deep-dive, behavioral, and HR questions anchored directly to your actual resume and target JD.",
  },
];

export const LandingPage: React.FC<LandingPageProps> = ({
  onEnterWorkspace,
  onOpenUpload,
  hasExistingResumes,
}) => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-slate-100">
      {/* Hero */}
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 w-[900px] h-[520px] rounded-full bg-indigo-600/20 blur-[140px]" />
        <div className="max-w-7xl mx-auto px-6 pt-16 pb-20 relative">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/25 text-indigo-600 dark:text-indigo-300 text-xs font-semibold mb-6">
              <ShieldCheck className="w-4 h-4" />
              Explainable NLP • Sentence Transformers • Zero-Fabrication Career Intelligence
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.08]">
              Turn Your Resume Into an{" "}
              <span className="bg-gradient-to-r from-indigo-500 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
                Evidence-Backed Career Twin
              </span>
            </h1>

            <p className="mt-6 text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl leading-relaxed">
              ResumeX AI goes far beyond generic keyword counters. Simulate ATS parsing, audit your profile like a skeptical recruiter, match against real job descriptions with neural embeddings, and prepare with resume-grounded interviews.
            </p>

            <div className="mt-9 flex flex-wrap items-center justify-center gap-4">
              <button
                onClick={onOpenUpload}
                className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-glow transition-all"
              >
                <Upload className="w-4 h-4" />
                Upload PDF / DOCX Resume
              </button>
              <button
                onClick={onEnterWorkspace}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white/80 dark:bg-navy-900/80 hover:border-indigo-500 font-semibold transition-all"
              >
                {hasExistingResumes ? "Open Intelligence Dashboard" : "Explore Workspace"}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Architecture Preview Strip */}
          <div className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="gradient-border-card p-5">
              <div className="flex items-center justify-between text-xs font-semibold text-indigo-500 uppercase tracking-wider">
                <span>Pipeline Stage 01</span>
                <Briefcase className="w-4 h-4" />
              </div>
              <h3 className="mt-2 font-bold text-base">In-Memory PDF/DOCX Intelligence</h3>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                PyMuPDF & python-docx extract layout risks, sections, metrics, and mask email/phone PII before persistence.
              </p>
            </div>
            <div className="gradient-border-card p-5">
              <div className="flex items-center justify-between text-xs font-semibold text-cyan-500 uppercase tracking-wider">
                <span>Pipeline Stage 02</span>
                <BrainCircuit className="w-4 h-4" />
              </div>
              <h3 className="mt-2 font-bold text-base">Bi-Encoder + spaCy Semantic Core</h3>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Combines 384-d SentenceTransformer embeddings, TF-IDF attribution, and entity recognition for reproducible scoring.
              </p>
            </div>
            <div className="gradient-border-card p-5">
              <div className="flex items-center justify-between text-xs font-semibold text-violet-500 uppercase tracking-wider">
                <span>Pipeline Stage 03</span>
                <GitCompare className="w-4 h-4" />
              </div>
              <h3 className="mt-2 font-bold text-base">Version & Career Twin Tracking</h3>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Track ATS & job-match gains across iterations and power personalized 30-60-90 day skill roadmaps.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Capabilities Grid */}
      <div className="max-w-7xl mx-auto px-6 pb-20">
        <div className="mb-8">
          <h2 className="text-2xl font-bold tracking-tight">
            Built Like a Commercial Career Intelligence Suite
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Every metric is deterministic, explainable, and computed from real uploaded documents.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {CAPABILITIES.map((cap) => {
            const Icon = cap.icon;
            return (
              <div
                key={cap.title}
                className="gradient-border-card p-6 hover:border-indigo-500/50 transition-all"
              >
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base">{cap.title}</h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {cap.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
