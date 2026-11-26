"""Intelligent Career Twin: evidence-backed digital representation of a candidate."""

from __future__ import annotations

from typing import Any

from app.services.career_predictor import predict_career_roles
from app.services.skill_roadmap import analyze_skill_gaps


def build_career_twin(
    parsed: dict[str, Any],
    ats_report: dict[str, Any],
    career_interests: list[str] | None = None,
    target_role: str | None = None,
) -> dict[str, Any]:
    """Synthesize a structured, evidence-based Career Twin graph and action engine."""
    years = float(parsed["estimated_years_experience"])
    projects_count = len(parsed["project_entries"])
    exp_count = len(parsed["experience_entries"])
    bullets = parsed["bullets"]
    quantified = parsed["bullet_stats"]["quantified"]

    if years >= 5.0:
        seniority = "Senior / Lead"
    elif years >= 2.0:
        seniority = "Mid-Level"
    elif years >= 0.5 or exp_count > 0:
        seniority = "Early Career / Junior"
    else:
        seniority = "Entry-Level / Student Builder"

    career_pred = predict_career_roles(parsed, career_interests=career_interests)
    primary_role = target_role or career_pred["top_role"]
    gap_analysis = analyze_skill_gaps(parsed, target_role=primary_role)

    detailed_skills = parsed["skills"]["detailed"]
    verified_nodes = [
        {
            "skill": s["skill"],
            "category": s["category"],
            "evidence_status": "verified",
            "strength": min(100, 65 + int(s["mentions"]) * 12),
            "mentions": s["mentions"],
        }
        for s in detailed_skills
        if s["evidenced_in_experience_or_projects"]
    ]
    declared_nodes = [
        {
            "skill": s["skill"],
            "category": s["category"],
            "evidence_status": "declared_only",
            "strength": min(60, 35 + int(s["mentions"]) * 8),
            "mentions": s["mentions"],
        }
        for s in detailed_skills
        if not s["evidenced_in_experience_or_projects"]
    ]

    total_skills = max(1, len(detailed_skills))
    evidence_depth_score = round((len(verified_nodes) / total_skills) * 100, 1)
    impact_density = round((quantified / max(1, len(bullets))) * 100, 1) if bullets else 0.0
    top_role_fit = float(career_pred["recommendations"][0]["fit_score"]) if career_pred["recommendations"] else 50.0
    ats_score = float(ats_report["overall_score"])

    twin_health_score = round(
        0.30 * ats_score
        + 0.25 * evidence_depth_score
        + 0.25 * top_role_fit
        + 0.20 * min(100.0, impact_density * 1.25),
        1,
    )

    skill_domain_distribution = [
        {
            "domain": category,
            "count": len(items),
            "verified_count": sum(1 for item in items if item in set(parsed["skills"]["evidenced_skills"])),
        }
        for category, items in parsed["skills"]["by_category"].items()
    ]

    thirty_sixty_ninety = [
        {
            "horizon": "Days 1-30: Evidence & Resume Upgrade",
            "focus": "Turn declared-only skills into verifiable proof and quantify existing bullets.",
            "actions": [
                *(
                    [f"Add project/work evidence for: {', '.join(s['skill'] for s in declared_nodes[:4])}."]
                    if declared_nodes
                    else ["All listed skills already have Experience/Project backing."]
                ),
                f"Quantify {max(0, len(bullets) - quantified)} unmeasured bullet(s) using real benchmarks.",
            ],
        },
        {
            "horizon": "Days 31-60: High-Priority Skill Bridging",
            "focus": f"Close top missing capabilities for {primary_role}.",
            "actions": [
                f"Learn & build with {g['skill']}: {g['project']}"
                for g in gap_analysis["technical_gaps"][:2]
            ]
            or [f"Deepen system design and testing depth for {primary_role}."],
        },
        {
            "horizon": "Days 61-90: Interview & Role Readiness",
            "focus": "Practice resume-grounded technical/behavioral stories and target applications.",
            "actions": [
                f"Rehearse architecture deep-dives for your {projects_count} project(s) and {exp_count} experience entry(ies).",
                f"Target {primary_role} roles (current fit index: {top_role_fit}%).",
            ],
        },
    ]

    return {
        "identity": {
            "candidate_label": parsed["contact"]["candidate_label"],
            "inferred_seniority": seniority,
            "years_experience": years,
            "primary_recommended_role": primary_role,
            "career_interests": career_interests or [],
            "organizations_detected": parsed["entities"]["organizations"][:6],
            "education_summary": parsed["education_entries"][:3],
        },
        "twin_health_score": twin_health_score,
        "readiness_radar": [
            {"metric": "ATS Readiness", "score": ats_score},
            {"metric": "Evidence Depth", "score": evidence_depth_score},
            {"metric": "Role Alignment", "score": top_role_fit},
            {"metric": "Impact Metrics", "score": impact_density},
            {
                "metric": "Portfolio Proof",
                "score": round(min(100.0, projects_count * 28.0 + exp_count * 25.0), 1),
            },
        ],
        "skill_graph": {
            "verified_skills": verified_nodes,
            "declared_only_skills": declared_nodes,
            "domain_distribution": skill_domain_distribution,
        },
        "evidence_pillars": {
            "experience_entries": parsed["experience_entries"],
            "project_entries": parsed["project_entries"],
            "certifications": parsed["certifications"],
            "quantified_achievements_count": quantified,
            "total_bullets_count": len(bullets),
        },
        "career_predictions": career_pred["recommendations"][:4],
        "priority_skill_gaps": gap_analysis["technical_gaps"][:5],
        "action_plan_30_60_90": thirty_sixty_ninety,
    }
