export interface ResumeSummary {
  id: number;
  profile_id: number;
  version_number: number;
  version_label: string;
  filename: string;
  file_type: string;
  word_count: number;
  page_count: number;
  ats_score: number;
  quality_grade: string;
  created_at: string;
}

export interface ATSDimension {
  key: string;
  label: string;
  weight: number;
  score: number;
  weighted_points: number;
  evidence: string[];
  recommendations: string[];
}

export interface ATSReport {
  overall_score: number;
  grade: string;
  pass_likelihood: string;
  dimensions: ATSDimension[];
  action_plan: {
    dimension: string;
    priority: string;
    recommendation: string;
    estimated_score_uplift: number;
  }[];
}

export interface RecruiterAudit {
  seven_second_scan: {
    inferred_experience_years: number;
    top_evidenced_skills: string[];
    projects_detected: number;
    experience_roles_detected: number;
    summary_present: boolean;
  };
  hiring_manager_verdict: string;
  verdict_reasoning: string;
  red_flags: {
    category: string;
    severity: "high" | "medium" | "low";
    detail: string;
    fix: string;
  }[];
  concerns: string[];
  unclear_bullets: { original: string; reason: string }[];
  recruiter_strength_signals: string[];
}

export interface ParsedResumeData {
  contact: {
    candidate_label: string;
    has_email: boolean;
    email_masked: string | null;
    has_phone: boolean;
    phone_masked: string | null;
    has_linkedin: boolean;
    linkedin_url: string | null;
    has_github: boolean;
    github_url: string | null;
  };
  layout: {
    page_count: number;
    word_count: number;
    avg_sentence_words: number;
    image_count: number;
    table_count: number;
    multi_column_risk: boolean;
  };
  sections_present: string[];
  missing_sections: string[];
  experience_entries: { title_line: string; highlights: string[] }[];
  project_entries: { title_line: string; highlights: string[] }[];
  education_entries: string[];
  certifications: string[];
  estimated_years_experience: number;
  entities: { organizations: string[]; locations: string[] };
  skills: {
    technical_skills: { skill: string; category: string; mentions: number }[];
    soft_skills: { skill: string; category: string; mentions: number }[];
    all_skills: string[];
    evidenced_skills: string[];
    unverified_skills: string[];
    by_category: Record<string, string[]>;
  };
  bullets: {
    section: string;
    text: string;
    word_count: number;
    action_verb: string;
    starts_with_strong_verb: boolean;
    has_metric: boolean;
    metrics_found: string[];
    weak_phrases: string[];
  }[];
  bullet_stats: {
    total: number;
    quantified: number;
    strong_verb: number;
    weak_phrasing: number;
  };
  diagnostics: {
    strengths: string[];
    weaknesses: string[];
    quality_summary: string;
  };
}

export interface ResumeDetail extends ResumeSummary {
  parsed_data: ParsedResumeData;
  ats_report: ATSReport;
  recruiter_audit: RecruiterAudit;
}

export interface DashboardOverview {
  has_data: boolean;
  summary_metrics: {
    total_versions: number;
    latest_ats_score: number;
    best_ats_score: number;
    total_job_matches: number;
    avg_job_match_score: number;
    interview_sessions_count: number;
    career_twin_health: number;
  };
  active_resume: {
    id: number;
    profile_id: number;
    version_label: string;
    filename: string;
    ats_score: number;
    quality_grade: string;
    technical_skills_count: number;
    evidenced_skills_count: number;
    bullet_stats: ParsedResumeData["bullet_stats"];
    ats_dimensions: ATSDimension[];
  } | null;
  ats_trend: {
    id: number;
    label: string;
    version_number: number;
    ats_score: number;
    grade: string;
    word_count: number;
    created_at: string;
  }[];
  skill_distribution: { category: string; total: number; evidenced: number }[];
  recent_job_matches: {
    id: number;
    job_title: string;
    company: string | null;
    overall_score: number;
    skill_coverage: number;
    semantic_similarity: number;
    created_at: string;
  }[];
  top_career_recommendations: CareerPredictionItem[];
  priority_recommendations: ATSReport["action_plan"];
}

export interface JobMatchResult {
  match_id?: number;
  job_title: string;
  company?: string | null;
  overall_match_score: number;
  compatibility_band: string;
  score_breakdown: {
    skill_coverage: { score: number; weight: number };
    semantic_similarity: {
      score: number;
      weight: number;
      dense_biencoder_score: number;
      tfidf_lexical_score: number;
      mode: string;
    };
    experience_alignment: {
      score: number;
      weight: number;
      candidate_years: number;
      required_years: number;
    };
  };
  matched_skills: string[];
  evidenced_matched_skills: string[];
  declared_only_matched_skills: string[];
  missing_skills: string[];
  missing_technical_skills: string[];
  missing_soft_skills: string[];
  top_shared_terms: { term: string; contribution: number }[];
  requirement_alignments: {
    requirement: string;
    best_resume_evidence: string;
    similarity_score: number;
    status: "strong" | "partial" | "gap";
  }[];
  recommendations: string[];
}

export interface SkillGapItem {
  skill: string;
  category: string;
  is_soft_skill: boolean;
  priority: "critical" | "high" | "recommended";
  reason: string;
  resource: string;
  url: string;
  project: string;
  hours: number;
}

export interface SkillGapResult {
  target_role_context: string;
  current_skill_count: number;
  evidenced_skill_count: number;
  skills_needing_project_evidence: string[];
  technical_gaps: SkillGapItem[];
  soft_gaps: SkillGapItem[];
  roadmap: {
    phase: string;
    goal: string;
    items: SkillGapItem[];
  }[];
  estimated_total_hours: number;
}

export interface BulletEnhancementResponse {
  count: number;
  policy: string;
  enhancements: {
    original: string;
    enhanced: string;
    changes_made: string[];
    has_verified_metric: boolean;
    metrics_prompt: string | null;
    fabrication_free: boolean;
  }[];
}

export interface CareerPredictionItem {
  role: string;
  summary: string;
  fit_score: number;
  confidence: string;
  semantic_alignment: number;
  matched_core_skills: string[];
  matched_preferred_skills: string[];
  evidenced_skills: string[];
  missing_core_skills: string[];
  reasoning: string[];
}

export interface CareerPredictionResponse {
  top_role: string;
  recommendations: CareerPredictionItem[];
  candidate_signals: {
    years_experience: number;
    projects_count: number;
    education_entries: string[];
    evidenced_skill_count: number;
  };
}

export interface InterviewQuestion {
  id: string;
  category: string;
  difficulty: string;
  question: string;
  grounded_in: string;
  what_interviewers_look_for: string[];
  answering_framework: string;
}

export interface InterviewResponse {
  session_id?: number;
  target_role: string;
  difficulty_mode: string;
  total_questions: number;
  category_breakdown: Record<string, number>;
  questions: InterviewQuestion[];
}

export interface CareerTwinData {
  snapshot_id?: number | null;
  resume_version_id: number;
  identity: {
    candidate_label: string;
    inferred_seniority: string;
    years_experience: number;
    primary_recommended_role: string;
    career_interests: string[];
    organizations_detected: string[];
    education_summary: string[];
  };
  twin_health_score: number;
  readiness_radar: { metric: string; score: number }[];
  skill_graph: {
    verified_skills: { skill: string; category: string; strength: number; mentions: number }[];
    declared_only_skills: { skill: string; category: string; strength: number; mentions: number }[];
    domain_distribution: { domain: string; count: number; verified_count: number }[];
  };
  evidence_pillars: {
    experience_entries: { title_line: string; highlights: string[] }[];
    project_entries: { title_line: string; highlights: string[] }[];
    certifications: string[];
    quantified_achievements_count: number;
    total_bullets_count: number;
  };
  career_predictions: CareerPredictionItem[];
  priority_skill_gaps: SkillGapItem[];
  action_plan_30_60_90: {
    horizon: string;
    focus: string;
    actions: string[];
  }[];
}

export interface VersionCompareResponse {
  base_version: {
    id: number;
    version_label: string;
    version_number: number;
    ats_score: number;
    quality_grade: string;
    word_count: number;
  };
  target_version: {
    id: number;
    version_label: string;
    version_number: number;
    ats_score: number;
    quality_grade: string;
    word_count: number;
  };
  ats_score_delta: number;
  summary: string;
  dimension_deltas: {
    key: string;
    label: string;
    base_score: number;
    target_score: number;
    delta: number;
  }[];
  skills_diff: {
    added: string[];
    removed: string[];
    newly_evidenced: string[];
    total_base: number;
    total_target: number;
  };
  bullet_quality_delta: {
    total_bullets_delta: number;
    quantified_bullets_delta: number;
    strong_verb_delta: number;
    weak_phrasing_delta: number;
  };
  sections_added: string[];
  sections_removed: string[];
  job_compatibility_delta: {
    base_match_score: number;
    target_match_score: number;
    delta: number;
    newly_matched_skills: string[];
    remaining_missing_skills: string[];
  } | null;
}
