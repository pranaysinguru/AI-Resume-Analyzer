"""Resume Version Intelligence: multi-version diffing and job compatibility tracking."""

from __future__ import annotations

from typing import Any

from app.models.entities import ResumeVersion
from app.services.job_matcher import match_resume_to_job


def compare_resume_versions(
    base: ResumeVersion,
    target: ResumeVersion,
    job_description: str | None = None,
) -> dict[str, Any]:
    """Compare two resume versions across ATS dimensions, skills, bullets, and optional JD fit."""
    base_parsed = base.parsed_data
    target_parsed = target.parsed_data

    base_dims = {d["key"]: d for d in base.ats_report.get("dimensions", [])}
    target_dims = {d["key"]: d for d in target.ats_report.get("dimensions", [])}

    dimension_deltas = []
    for key, t_dim in target_dims.items():
        b_dim = base_dims.get(key, {"score": 0.0, "label": t_dim["label"]})
        dimension_deltas.append(
            {
                "key": key,
                "label": t_dim["label"],
                "base_score": b_dim["score"],
                "target_score": t_dim["score"],
                "delta": round(float(t_dim["score"]) - float(b_dim["score"]), 1),
            }
        )

    base_skills = set(base_parsed["skills"]["all_skills"])
    target_skills = set(target_parsed["skills"]["all_skills"])
    base_evidenced = set(base_parsed["skills"]["evidenced_skills"])
    target_evidenced = set(target_parsed["skills"]["evidenced_skills"])

    b_bullets = base_parsed["bullet_stats"]
    t_bullets = target_parsed["bullet_stats"]

    job_compatibility_delta = None
    if job_description and job_description.strip():
        base_match = match_resume_to_job(base_parsed, "Target Role", job_description)
        target_match = match_resume_to_job(target_parsed, "Target Role", job_description)
        job_compatibility_delta = {
            "base_match_score": base_match["overall_match_score"],
            "target_match_score": target_match["overall_match_score"],
            "delta": round(target_match["overall_match_score"] - base_match["overall_match_score"], 1),
            "newly_matched_skills": sorted(set(target_match["matched_skills"]) - set(base_match["matched_skills"])),
            "remaining_missing_skills": target_match["missing_skills"],
        }

    ats_delta = round(float(target.ats_score) - float(base.ats_score), 1)
    summary = (
        f"'{target.version_label}' improved ATS score by +{ats_delta} pts ({base.ats_score} -> {target.ats_score})."
        if ats_delta > 0
        else f"'{target.version_label}' changed ATS score by {ats_delta} pts ({base.ats_score} -> {target.ats_score})."
        if ats_delta < 0
        else f"'{target.version_label}' maintains the same ATS score ({target.ats_score})."
    )

    return {
        "base_version": {
            "id": base.id,
            "version_label": base.version_label,
            "version_number": base.version_number,
            "ats_score": base.ats_score,
            "quality_grade": base.quality_grade,
            "word_count": base.word_count,
        },
        "target_version": {
            "id": target.id,
            "version_label": target.version_label,
            "version_number": target.version_number,
            "ats_score": target.ats_score,
            "quality_grade": target.quality_grade,
            "word_count": target.word_count,
        },
        "ats_score_delta": ats_delta,
        "summary": summary,
        "dimension_deltas": dimension_deltas,
        "skills_diff": {
            "added": sorted(target_skills - base_skills),
            "removed": sorted(base_skills - target_skills),
            "newly_evidenced": sorted(target_evidenced - base_evidenced),
            "total_base": len(base_skills),
            "total_target": len(target_skills),
        },
        "bullet_quality_delta": {
            "total_bullets_delta": t_bullets["total"] - b_bullets["total"],
            "quantified_bullets_delta": t_bullets["quantified"] - b_bullets["quantified"],
            "strong_verb_delta": t_bullets["strong_verb"] - b_bullets["strong_verb"],
            "weak_phrasing_delta": t_bullets["weak_phrasing"] - b_bullets["weak_phrasing"],
        },
        "sections_added": sorted(set(target_parsed["sections_present"]) - set(base_parsed["sections_present"])),
        "sections_removed": sorted(set(base_parsed["sections_present"]) - set(target_parsed["sections_present"])),
        "job_compatibility_delta": job_compatibility_delta,
    }
