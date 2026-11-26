"""Explainable Career Prediction & Role Recommendation service."""

from __future__ import annotations

from typing import Any

from app.nlp.embeddings import batch_dense_similarity
from app.nlp.skill_taxonomy import ROLE_PROFILES


def predict_career_roles(
    parsed: dict[str, Any],
    career_interests: list[str] | None = None,
) -> dict[str, Any]:
    """Recommend best-fit career roles with transparent skill, semantic, and evidence reasoning."""
    resume_skills = set(parsed["skills"]["all_skills"])
    evidenced_skills = set(parsed["skills"]["evidenced_skills"])
    interests = [i.strip().lower() for i in (career_interests or []) if i.strip()]

    role_texts = [
        f"{p.role}. {p.summary} Core skills: {', '.join(p.core_skills)}. {p.avg_project_signal}"
        for p in ROLE_PROFILES
    ]
    semantic_scores = batch_dense_similarity(parsed["sanitized_text"][:3000], role_texts)

    predictions: list[dict[str, Any]] = []
    for idx, profile in enumerate(ROLE_PROFILES):
        core_matched = [s for s in profile.core_skills if s in resume_skills]
        pref_matched = [s for s in profile.preferred_skills if s in resume_skills]
        evidenced_core = [s for s in core_matched if s in evidenced_skills]

        core_ratio = len(core_matched) / max(1, len(profile.core_skills))
        pref_ratio = len(pref_matched) / max(1, len(profile.preferred_skills))
        evidence_bonus = (len(evidenced_core) / max(1, len(profile.core_skills))) * 12.0
        sem_score = semantic_scores[idx]

        interest_boost = 0.0
        matched_interest = None
        for interest in interests:
            if interest in profile.role.lower() or any(interest in sk.lower() for sk in profile.core_skills):
                interest_boost = 6.0
                matched_interest = interest
                break

        fit_score = round(
            min(
                99.0,
                core_ratio * 48.0 + pref_ratio * 18.0 + (sem_score / 100.0) * 22.0 + evidence_bonus + interest_boost,
            ),
            1,
        )

        missing_core = [s for s in profile.core_skills if s not in resume_skills]
        reasons: list[str] = []
        if core_matched:
            reasons.append(
                f"Matches {len(core_matched)}/{len(profile.core_skills)} core skills ({', '.join(core_matched[:5])})."
            )
        if evidenced_core:
            reasons.append(
                f"Demonstrated hands-on experience/projects using {', '.join(evidenced_core[:4])}."
            )
        if pref_matched:
            reasons.append(f"Bonus alignment in preferred stack: {', '.join(pref_matched[:4])}.")
        if matched_interest:
            reasons.append(f"Aligns with your stated career interest ('{matched_interest}').")
        if missing_core:
            reasons.append(f"Adding {', '.join(missing_core[:3])} would raise competitiveness significantly.")

        predictions.append(
            {
                "role": profile.role,
                "summary": profile.summary,
                "fit_score": fit_score,
                "confidence": "High" if fit_score >= 68 else "Moderate" if fit_score >= 48 else "Exploratory",
                "semantic_alignment": sem_score,
                "matched_core_skills": core_matched,
                "matched_preferred_skills": pref_matched,
                "evidenced_skills": evidenced_core,
                "missing_core_skills": missing_core,
                "reasoning": reasons,
            }
        )

    predictions.sort(key=lambda item: item["fit_score"], reverse=True)
    return {
        "top_role": predictions[0]["role"] if predictions else "Software Engineer",
        "recommendations": predictions[:5],
        "candidate_signals": {
            "years_experience": parsed["estimated_years_experience"],
            "projects_count": len(parsed["project_entries"]),
            "education_entries": parsed["education_entries"][:2],
            "evidenced_skill_count": len(evidenced_skills),
        },
    }
