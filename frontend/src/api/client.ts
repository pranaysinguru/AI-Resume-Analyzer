import type {
  BulletEnhancementResponse,
  CareerPredictionResponse,
  CareerTwinData,
  DashboardOverview,
  InterviewResponse,
  JobMatchResult,
  ResumeDetail,
  ResumeSummary,
  SkillGapResult,
  VersionCompareResponse,
} from "../types/api";

const API_BASE = "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data?.detail === "string") {
        message = data.detail;
      }
    } catch {
      // ignore non-json body
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listResumes: () => request<ResumeSummary[]>("/resumes"),

  getResume: (id: number) => request<ResumeDetail>(`/resumes/${id}`),

  deleteResume: (id: number) =>
    request<{ deleted: boolean; id: number }>(`/resumes/${id}`, { method: "DELETE" }),

  uploadResume: (
    file: File,
    opts?: { profileId?: number; versionLabel?: string; targetRole?: string }
  ) => {
    const form = new FormData();
    form.append("file", file);
    if (opts?.profileId !== undefined) form.append("profile_id", String(opts.profileId));
    if (opts?.versionLabel) form.append("version_label", opts.versionLabel);
    if (opts?.targetRole) form.append("target_role", opts.targetRole);
    return request<ResumeDetail>("/resumes/upload", { method: "POST", body: form });
  },

  getDashboard: (resumeId?: number) =>
    request<DashboardOverview>(
      resumeId ? `/dashboard/overview?resume_id=${resumeId}` : "/dashboard/overview"
    ),

  enhanceBullets: (payload: {
    resume_version_id?: number;
    bullets?: string[];
    target_role?: string;
  }) =>
    request<BulletEnhancementResponse>("/analysis/enhance-bullets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  runJobMatch: (payload: {
    resume_version_id: number;
    job_title: string;
    company?: string;
    job_description: string;
  }) =>
    request<JobMatchResult>("/matching/job-match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  getMatchHistory: (resumeId?: number) =>
    request<
      {
        id: number;
        resume_version_id: number;
        job_title: string;
        company: string | null;
        overall_score: number;
        semantic_similarity: number;
        skill_coverage: number;
        experience_alignment: number;
        matched_skills: string[];
        missing_skills: string[];
        created_at: string;
      }[]
    >(resumeId ? `/matching/history?resume_version_id=${resumeId}` : "/matching/history"),

  analyzeSkillGaps: (payload: {
    resume_version_id: number;
    target_role?: string;
    job_description?: string;
  }) =>
    request<SkillGapResult>("/matching/skill-gaps", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  predictCareer: (payload: { resume_version_id: number; career_interests: string[] }) =>
    request<CareerPredictionResponse>("/matching/career-predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  generateInterview: (payload: {
    resume_version_id: number;
    target_role: string;
    job_description?: string;
    difficulty: "junior" | "mid" | "senior" | "mixed";
  }) =>
    request<InterviewResponse>("/interview/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  getLatestTwin: (resumeId: number) => request<CareerTwinData>(`/twin/latest/${resumeId}`),

  synthesizeTwin: (payload: {
    resume_version_id: number;
    career_interests: string[];
    target_role?: string;
  }) =>
    request<CareerTwinData>("/twin/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  compareVersions: (payload: {
    base_version_id: number;
    target_version_id: number;
    job_description?: string;
  }) =>
    request<VersionCompareResponse>("/resumes/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
};
