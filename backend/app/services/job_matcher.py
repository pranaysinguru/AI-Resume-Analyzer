"""Explainable AI Job Matching service combining dense semantics, TF-IDF, and skill alignment."""

from __future__ import annotations

import re
from typing import Any

from app.nlp.embeddings import batch_dense_similarity, compute_semantic_similarity
from app.nlp.skill_taxonomy import extract_skills

YEARS_REQ_RE = re.compile(r"(\d+)\+?\s*(?:-\s*\d+\s*)?years?\s+(?:of\s+)?experience", re.IGNORECASE)


def _split_jd_requirements(job_description: str) -> list[str]:
    lines = []
    for raw in re.split(r"[\n•●▪\-*]+", job_description):
        clean = re.sub(r"\s+", " ", raw).strip(" .:-")
        if 5 <= len(clean.split()) <= 35:
            lines.append(clean)
    return lines[:12]


def match_resume_to_job(parsed: dict[str, Any], job_title: str, job_description: str) -> dict[str, Any]:
    """Compare a parsed resume against a job description with full score explainability."""
    resume_text = parsed["sanitized_text"]
    jd_skills = extract_skills(job_description)
    resume_skills_all = set(parsed["skills"]["all_skills"])
    resume_evidenced = set(parsed["skills"]["evidenced_skills"])

    jd_all_skills = jd_skills["all_skills"]
    matched_skills = [s for s in jd_all_skills if s in resume_skills_all]
    missing_skills = [s for s in jd_all_skills if s not in resume_skills_all]
    evidenced_matches = [s for s in matched_skills if s in resume_evidenced]
    declared_only_matches = [s for s in matched_skills if s not in resume_evidenced]

    if jd_all_skills:
        # Evidenced matches carry full weight; declared-only matches carry 0.7x weight
        weighted_hits = len(evidenced_matches) + 0.7 * len(declared_only_matches)
        skill_coverage = round(min(100.0, (weighted_hits / len(jd_all_skills)) * 100.0), 1)
    else:
        skill_coverage = 70.0

    # Semantic similarity across full resume and key sections
    full_sim = compute_semantic_similarity(resume_text, f"{job_title}\n{job_description}")
    exp_proj_text = "\n".join(
        parsed["section_contents"].get("experience", []) + parsed["section_contents"].get("projects", [])
    )
    exp_sim = (
        compute_semantic_similarity(exp_proj_text, job_description)["hybrid_score"]
        if exp_proj_text.strip()
        else full_sim["hybrid_score"]
    )
    semantic_score = round(0.6 * float(full_sim["hybrid_score"]) + 0.4 * float(exp_sim), 1)

    # Experience alignment
    candidate_years = float(parsed["estimated_years_experience"])
    req_years_matches = [int(m) for m in YEARS_REQ_RE.findall(job_description)]
    required_years = max(req_years_matches) if req_years_matches else 0
    if required_years == 0:
        experience_alignment = 85.0 if (candidate_years > 0 or len(parsed["project_entries"]) >= 2) else 65.0
    elif candidate_years >= required_years:
        experience_alignment = 100.0
    else:
        ratio = candidate_years / max(1, required_years)
        project_bonus = min(15.0, len(parsed["project_entries"]) * 5.0)
        experience_alignment = round(min(95.0, ratio * 85.0 + project_bonus), 1)

    overall_score = round(
        0.44 * skill_coverage + 0.41 * semantic_score + 0.15 * experience_alignment,
        1,
    )

    # Map each JD requirement to the strongest matching resume bullet/entry
    jd_requirements = _split_jd_requirements(job_description)
    evidence_pool = [b["text"] for b in parsed["bullets"]]
    if not evidence_pool:
        evidence_pool = [
            line
            for sec in ("experience", "projects", "skills", "education")
            for line in parsed["section_contents"].get(sec, [])
        ][:20]

    requirement_alignments: list[dict[str, Any]] = []
    if jd_requirements and evidence_pool:
        for req in jd_requirements[:8]:
            sims = batch_dense_similarity(req, evidence_pool)
            best_idx = max(range(len(sims)), key=lambda i: sims[i])
            best_score = sims[best_idx]
            requirement_alignments.append(
                {
                    "requirement": req,
                    "best_resume_evidence": evidence_pool[best_idx],
                    "similarity_score": best_score,
                    "status": "strong" if best_score >= 52 else "partial" if best_score >= 34 else "gap",
                }
            )

    return {
        "job_title": job_title,
        "overall_match_score": overall_score,
        "compatibility_band": (
            "Strong Fit"
            if overall_score >= 75
            else "Competitive Fit"
            if overall_score >= 58
            else "Developing Fit"
        ),
        "score_breakdown": {
            "skill_coverage": {"score": skill_coverage, "weight": 0.44},
            "semantic_similarity": {
                "score": semantic_score,
                "weight": 0.41,
                "dense_biencoder_score": full_sim["dense_similarity"],
                "tfidf_lexical_score": full_sim["lexical_similarity"],
                "mode": full_sim["mode"],
            },
            "experience_alignment": {
                "score": experience_alignment,
                "weight": 0.15,
                "candidate_years": candidate_years,
                "required_years": required_years,
            },
        },
        "matched_skills": matched_skills,
        "evidenced_matched_skills": evidenced_matches,
        "declared_only_matched_skills": declared_only_matches,
        "missing_skills": missing_skills,
        "missing_technical_skills": [
            s["skill"] for s in jd_skills["technical_skills"] if s["skill"] not in resume_skills_all
        ],
        "missing_soft_skills": [
            s["skill"] for s in jd_skills["soft_skills"] if s["skill"] not in resume_skills_all
        ],
        "top_shared_terms": full_sim["top_contributing_terms"],
        "requirement_alignments": requirement_alignments,
        "recommendations": [
            *(
                [f"Incorporate missing high-priority JD skills through real projects: {', '.join(missing_skills[:5])}."]
                if missing_skills
                else ["Your skill set covers all detected keywords in this job description."]
            ),
            *(
                [f"Add concrete bullet evidence for matched but unverified skills: {', '.join(declared_only_matches[:4])}."]
                if declared_only_matches
                else []
            ),
            "Tailor your top Summary and first 3 Experience/Project bullets to mirror the exact problem domain of this JD.",
        ],
    }
