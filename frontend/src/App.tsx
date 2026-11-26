import React, { useCallback, useEffect, useState } from "react";
import {
  BrainCircuit,
  FileSearch,
  GitCompare,
  Home,
  LayoutDashboard,
  Menu,
  MessageSquareCode,
  Moon,
  Sun,
  Target,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import { api } from "./api/client";
import { LandingPage } from "./components/LandingPage";
import { UploadModal } from "./components/UploadModal";
import { AnalyzerPage } from "./pages/AnalyzerPage";
import { CareerTwinPage } from "./pages/CareerTwinPage";
import { DashboardPage } from "./pages/DashboardPage";
import { InterviewPage } from "./pages/InterviewPage";
import { JobMatchPage } from "./pages/JobMatchPage";
import { VersionsPage } from "./pages/VersionsPage";
import type { DashboardOverview, ResumeDetail, ResumeSummary } from "./types/api";

type NavTab =
  | "landing"
  | "dashboard"
  | "analyzer"
  | "job-match"
  | "career-twin"
  | "interview"
  | "versions";

const NAV_ITEMS: { id: Exclude<NavTab, "landing">; label: string; icon: React.ElementType }[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "analyzer", label: "Resume & ATS", icon: FileSearch },
  { id: "job-match", label: "Job Match & Gaps", icon: Target },
  { id: "career-twin", label: "Career Twin", icon: BrainCircuit },
  { id: "interview", label: "AI Interview", icon: MessageSquareCode },
  { id: "versions", label: "Version Diff", icon: GitCompare },
];

export function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState<NavTab>("landing");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);

  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [activeResume, setActiveResume] = useState<ResumeDetail | null>(null);
  const [dashboard, setDashboard] = useState<DashboardOverview | null>(null);
  const [loadingDash, setLoadingDash] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const refreshAll = useCallback(async (preferredId?: number) => {
    setLoadingDash(true);
    setApiError(null);
    try {
      const list = await api.listResumes();
      setResumes(list);
      const targetId = preferredId ?? (list[0]?.id ?? null);
      setSelectedResumeId(targetId);

      const [dashData, detailData] = await Promise.all([
        api.getDashboard(targetId ?? undefined),
        targetId ? api.getResume(targetId) : Promise.resolve(null),
      ]);
      setDashboard(dashData);
      setActiveResume(detailData);
    } catch (err) {
      setApiError(
        err instanceof Error
          ? err.message
          : "Unable to connect to ResumeX AI backend."
      );
    } finally {
      setLoadingDash(false);
    }
  }, []);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const handleSelectResume = async (id: number) => {
    setSelectedResumeId(id);
    try {
      const [detail, dash] = await Promise.all([
        api.getResume(id),
        api.getDashboard(id),
      ]);
      setActiveResume(detail);
      setDashboard(dash);
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Failed to load resume.");
    }
  };

  const handleDeleteActive = async () => {
    if (!selectedResumeId) return;
    try {
      await api.deleteResume(selectedResumeId);
      await refreshAll();
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Delete failed.");
    }
  };

  const handleUploaded = async (uploaded: ResumeDetail) => {
    setActiveTab("dashboard");
    await refreshAll(uploaded.id);
  };

  if (activeTab === "landing") {
    return (
      <>
        <header className="sticky top-0 z-40 border-b border-slate-200/70 dark:border-slate-800/80 bg-white/80 dark:bg-navy-950/80 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-extrabold shadow">
                RX
              </div>
              <span className="font-extrabold text-lg tracking-tight">
                ResumeX <span className="text-indigo-500">AI</span>
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setDarkMode((d) => !d)}
                aria-label="Toggle color theme"
                className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-navy-900"
              >
                {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setActiveTab("dashboard")}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
              >
                Open App
              </button>
            </div>
          </div>
        </header>

        <LandingPage
          onEnterWorkspace={() => setActiveTab("dashboard")}
          onOpenUpload={() => setUploadOpen(true)}
          hasExistingResumes={resumes.length > 0}
        />

        <UploadModal
          open={uploadOpen}
          onClose={() => setUploadOpen(false)}
          existingResumes={resumes}
          onUploaded={handleUploaded}
        />
      </>
    );
  }

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-slate-100">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-200 lg:static lg:translate-x-0 bg-white dark:bg-navy-900 border-r border-slate-200 dark:border-slate-800 flex flex-col ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="h-16 px-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800">
          <button
            onClick={() => setActiveTab("landing")}
            className="flex items-center gap-2.5 text-left"
          >
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-extrabold text-sm">
              RX
            </div>
            <span className="font-extrabold tracking-tight">
              ResumeX <span className="text-indigo-500">AI</span>
            </span>
          </button>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-1 text-slate-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 border-b border-slate-200 dark:border-slate-800 space-y-2">
          <button
            onClick={() => setUploadOpen(true)}
            className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-glow transition-all"
          >
            <Upload className="w-4 h-4" />
            Upload Resume
          </button>

          {resumes.length > 0 && (
            <div className="pt-2 space-y-1.5">
              <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Active Resume
              </label>
              <div className="flex items-center gap-1">
                <select
                  value={selectedResumeId ?? ""}
                  onChange={(e) => handleSelectResume(Number(e.target.value))}
                  aria-label="Active resume version selector"
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 px-2.5 py-1.5 text-xs truncate"
                >
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.version_label} ({r.ats_score})
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleDeleteActive}
                  title="Delete selected resume"
                  aria-label="Delete selected resume"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-500/10"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  active
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-navy-800"
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="p-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <button
            onClick={() => setActiveTab("landing")}
            className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-500"
          >
            <Home className="w-3.5 h-3.5" />
            Landing
          </button>
          <button
            onClick={() => setDarkMode((d) => !d)}
            aria-label="Toggle theme"
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-navy-800 text-slate-500"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="lg:hidden h-14 px-4 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-navy-900">
          <button
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Open navigation menu"
            className="p-2 rounded-lg"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="font-bold text-sm">ResumeX AI</span>
          <button
            onClick={() => setUploadOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold"
          >
            Upload
          </button>
        </header>

        <main className="flex-1 p-5 sm:p-8 max-w-7xl w-full mx-auto">
          {apiError && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-500">
              {apiError}
            </div>
          )}

          {activeTab === "dashboard" && (
            <DashboardPage
              data={dashboard}
              loading={loadingDash}
              onOpenUpload={() => setUploadOpen(true)}
              onNavigate={(tab) => setActiveTab(tab as NavTab)}
            />
          )}
          {activeTab === "analyzer" && (
            <AnalyzerPage
              resume={activeResume}
              onOpenUpload={() => setUploadOpen(true)}
            />
          )}
          {activeTab === "job-match" && (
            <JobMatchPage
              resume={activeResume}
              onOpenUpload={() => setUploadOpen(true)}
              onMatchSaved={() => refreshAll(selectedResumeId ?? undefined)}
            />
          )}
          {activeTab === "career-twin" && (
            <CareerTwinPage
              resume={activeResume}
              onOpenUpload={() => setUploadOpen(true)}
            />
          )}
          {activeTab === "interview" && (
            <InterviewPage
              resume={activeResume}
              onOpenUpload={() => setUploadOpen(true)}
              onSessionCreated={() => refreshAll(selectedResumeId ?? undefined)}
            />
          )}
          {activeTab === "versions" && (
            <VersionsPage
              resumes={resumes}
              onOpenUpload={() => setUploadOpen(true)}
            />
          )}
        </main>
      </div>

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        existingResumes={resumes}
        onUploaded={handleUploaded}
      />
    </div>
  );
}

export default App;
