"""Skill Gap Intelligence & Personalized Learning Roadmap generator."""

from __future__ import annotations

from typing import Any

from app.nlp.skill_taxonomy import (
    ROLE_PROFILES,
    SKILL_TO_CATEGORY,
    SOFT_SKILL_CATEGORIES,
    extract_skills,
    get_learning_recommendation,
)


def analyze_skill_gaps(
    parsed: dict[str, Any],
    target_role: str | None = None,
    job_description: str | None = None,
) -> dict[str, Any]:
    """Identify and prioritize technical/soft skill gaps and generate a learning roadmap."""
    resume_skills = set(parsed["skills"]["all_skills"])
    evidenced_skills = set(parsed["skills"]["evidenced_skills"])

    matched_role = None
    if target_role:
        for profile in ROLE_PROFILES:
            if target_role.lower() in profile.role.lower() or profile.role.lower() in target_role.lower():
                matched_role = profile
                break

    prioritized_gaps: list[dict[str, Any]] = []
    seen_skills: set[str] = set()

    if job_description and job_description.strip():
        jd_extracted = extract_skills(job_description)
        for item in jd_extracted["technical_skills"] + jd_extracted["soft_skills"]:
            skill_name = str(item["skill"])
            if skill_name not in resume_skills and skill_name not in seen_skills:
                seen_skills.add(skill_name)
                mentions = int(item["mentions"])
                priority = "critical" if mentions >= 2 or not item["is_soft_skill"] else "high"
                rec = get_learning_recommendation(skill_name)
                prioritized_gaps.append(
                    {
                        "skill": skill_name,
                        "category": item["category"],
                        "is_soft_skill": bool(item["is_soft_skill"]),
                        "priority": priority,
                        "reason": f"Explicitly requested in target Job Description ({mentions} mention(s)).",
                        **rec,
                    }
                )

    role_profile = matched_role or ROLE_PROFILES[1]  # Default Full Stack if none matched
    for skill_name in role_profile.core_skills:
        if skill_name not in resume_skills and skill_name not in seen_skills:
            seen_skills.add(skill_name)
            cat = SKILL_TO_CATEGORY.get(skill_name, "Core Technical")
            rec = get_learning_recommendation(skill_name)
            prioritized_gaps.append(
                {
                    "skill": skill_name,
                    "category": cat,
                    "is_soft_skill": cat in SOFT_SKILL_CATEGORIES,
                    "priority": "critical",
                    "reason": f"Core competency required for {role_profile.role}.",
                    **rec,
                }
            )

    for skill_name in role_profile.preferred_skills + role_profile.soft_skills:
        if skill_name not in resume_skills and skill_name not in seen_skills:
            seen_skills.add(skill_name)
            cat = SKILL_TO_CATEGORY.get(skill_name, "Preferred")
            rec = get_learning_recommendation(skill_name)
            prioritized_gaps.append(
                {
                    "skill": skill_name,
                    "category": cat,
                    "is_soft_skill": cat in SOFT_SKILL_CATEGORIES,
                    "priority": "high" if cat not in SOFT_SKILL_CATEGORIES else "recommended",
                    "reason": f"High-leverage differentiator for {role_profile.role}.",
                    **rec,
                }
            )

    priority_order = {"critical": 0, "high": 1, "recommended": 2}
    prioritized_gaps.sort(key=lambda g: (priority_order[g["priority"]], g["is_soft_skill"], g["skill"]))

    technical_gaps = [g for g in prioritized_gaps if not g["is_soft_skill"]]
    soft_gaps = [g for g in prioritized_gaps if g["is_soft_skill"]]
    skills_needing_evidence = sorted(resume_skills - evidenced_skills)

    roadmap_phases = [
        {
            "phase": "Phase 1 (Weeks 1-2): Critical Core Gaps",
            "goal": "Close must-have missing technical foundations and prove them with runnable code.",
            "items": [g for g in prioritized_gaps if g["priority"] == "critical"][:4],
        },
        {
            "phase": "Phase 2 (Weeks 3-4): Architecture & Differentiators",
            "goal": "Add production readiness (testing, containers, cloud, or ML evals).",
            "items": [g for g in prioritized_gaps if g["priority"] == "high"][:4],
        },
        {
            "phase": "Phase 3 (Weeks 5-6): Portfolio Proof & Soft Skills",
            "goal": "Ship a capstone project and document measurable benchmarks on your resume.",
            "items": [g for g in prioritized_gaps if g["priority"] == "recommended"][:4],
        },
    ]

    total_hours = sum(int(g.get("hours", 10)) for g in prioritized_gaps[:10])
    return {
        "target_role_context": target_role or role_profile.role,
        "current_skill_count": len(resume_skills),
        "evidenced_skill_count": len(evidenced_skills),
        "skills_needing_project_evidence": skills_needing_evidence,
        "technical_gaps": technical_gaps,
        "soft_gaps": soft_gaps,
        "roadmap": roadmap_phases,
        "estimated_total_hours": total_hours,
    }
