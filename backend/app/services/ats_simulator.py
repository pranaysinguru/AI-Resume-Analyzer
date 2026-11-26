"""Explainable Intelligent ATS Simulator."""

from __future__ import annotations

from typing import Any


def _grade_from_score(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 82:
        return "A"
    if score >= 74:
        return "B+"
    if score >= 65:
        return "B"
    if score >= 52:
        return "C"
    return "D"


def simulate_ats(parsed: dict[str, Any]) -> dict[str, Any]:
    """Compute an explainable, reproducible ATS compatibility report."""
    layout = parsed["layout"]
    contact = parsed["contact"]
    sections = parsed["sections_present"]
    missing_sections = parsed["missing_sections"]
    skills = parsed["skills"]
    bullet_stats = parsed["bullet_stats"]

    # 1. Formatting & Layout (20%)
    fmt_score = 100.0
    fmt_evidence: list[str] = []
    fmt_recs: list[str] = []

    page_count = int(layout["page_count"])
    word_count = int(layout["word_count"])
    if page_count > 2:
        fmt_score -= 18
        fmt_recs.append(f"Condense resume from {page_count} pages to 1-2 pages for standard ATS screening.")
    else:
        fmt_evidence.append(f"Optimal length: {page_count} page(s).")

    if word_count < 220:
        fmt_score -= 22
        fmt_recs.append("Resume is too sparse (<220 words); expand project and experience details.")
    elif word_count > 1100:
        fmt_score -= 14
        fmt_recs.append("Resume exceeds 1,100 words; trim older or redundant bullets for tighter signal.")
    else:
        fmt_evidence.append(f"Healthy content density ({word_count} words).")

    if layout["multi_column_risk"]:
        fmt_score -= 18
        fmt_recs.append("Avoid multi-column layouts or nested tables; use a single-column reading order.")
    else:
        fmt_evidence.append("Clean single-column reading flow detected.")

    if int(layout["image_count"]) > 1:
        fmt_score -= 10
        fmt_recs.append("Remove embedded photos, icons, or charts; ATS parsers ignore image text.")

    fmt_score = max(0.0, min(100.0, round(fmt_score, 1)))

    # 2. Section Completeness & Contactability (20%)
    core_sections = ["summary", "experience", "projects", "education", "skills"]
    present_core = [s for s in core_sections if s in sections]
    sec_score = (len(present_core) / len(core_sections)) * 75.0
    if contact["has_email"]:
        sec_score += 10
    if contact["has_phone"]:
        sec_score += 7.5
    if contact["has_linkedin"] or contact["has_github"]:
        sec_score += 7.5
    sec_score = round(min(100.0, sec_score), 1)

    sec_evidence = [f"Detected {len(present_core)}/{len(core_sections)} core sections ({', '.join(present_core) or 'none'})."]
    sec_recs: list[str] = []
    if missing_sections:
        sec_recs.append(f"Add missing core section(s): {', '.join(missing_sections)}.")
    if not contact["has_email"] or not contact["has_phone"]:
        sec_recs.append("Include both a professional email address and phone number in the header.")
    if not (contact["has_linkedin"] or contact["has_github"]):
        sec_recs.append("Add clickable LinkedIn and GitHub URLs so recruiters and ATS enrich your profile.")

    # 3. Keyword & Skill Signal (25%)
    tech_count = len(skills["technical_skills"])
    soft_count = len(skills["soft_skills"])
    evidenced_count = len(skills["evidenced_skills"])
    total_skills = max(1, len(skills["all_skills"]))
    evidence_ratio = evidenced_count / total_skills

    kw_score = (
        min(tech_count / 12.0, 1.0) * 50.0
        + min(soft_count / 3.0, 1.0) * 15.0
        + evidence_ratio * 35.0
    )
    kw_score = round(min(100.0, kw_score), 1)
    kw_evidence = [
        f"{tech_count} technical skills and {soft_count} soft/leadership skills extracted.",
        f"{evidenced_count}/{len(skills['all_skills'])} listed skills are backed by Experience/Project context ({round(evidence_ratio * 100)}%).",
    ]
    kw_recs: list[str] = []
    if tech_count < 8:
        kw_recs.append("Include more domain-specific technical keywords (frameworks, databases, cloud, testing).")
    if skills["unverified_skills"]:
        sample = ", ".join(skills["unverified_skills"][:5])
        kw_recs.append(f"Back up listed skills ({sample}) with explicit bullets in Experience or Projects.")

    # 4. Impact & Achievements (25%)
    total_bullets = bullet_stats["total"]
    if total_bullets == 0:
        imp_score = 25.0
        imp_evidence = ["No structured accomplishment bullets were detected under Experience or Projects."]
        imp_recs = ["Rewrite Experience and Project paragraphs as concise bullet points starting with strong action verbs and numbers."]
    else:
        metric_ratio = bullet_stats["quantified"] / total_bullets
        verb_ratio = bullet_stats["strong_verb"] / total_bullets
        weak_penalty = min(20.0, bullet_stats["weak_phrasing"] * 5.0)
        imp_score = max(
            0.0,
            min(100.0, 20.0 + metric_ratio * 45.0 + verb_ratio * 35.0 - weak_penalty),
        )
        imp_score = round(imp_score, 1)
        imp_evidence = [
            f"{bullet_stats['quantified']}/{total_bullets} bullets include measurable metrics ({round(metric_ratio * 100)}%).",
            f"{bullet_stats['strong_verb']}/{total_bullets} bullets start with strong action verbs.",
        ]
        imp_recs = []
        if metric_ratio < 0.5:
            imp_recs.append("Quantify impact in more bullets (e.g., latency %, revenue/cost impact, throughput, test coverage, user scale).")
        if verb_ratio < 0.7:
            imp_recs.append("Start every bullet with a high-ownership verb (Engineered, Architected, Automated, Reduced).")
        if bullet_stats["weak_phrasing"] > 0:
            imp_recs.append("Replace passive phrases ('responsible for', 'worked on') with direct execution verbs.")

    # 5. Readability & Conciseness (10%)
    avg_sent = float(layout["avg_sentence_words"])
    read_score = 100.0
    read_evidence = [f"Average sentence/bullet length: {avg_sent} words."]
    read_recs: list[str] = []
    if avg_sent > 26:
        read_score -= 22
        read_recs.append("Shorten dense sentences (>26 words average) into crisp single-idea bullets.")
    elif avg_sent < 7:
        read_score -= 15
        read_recs.append("Provide fuller context in bullets—current phrases are overly terse.")
    read_score = max(0.0, min(100.0, round(read_score, 1)))

    dimensions = [
        {
            "key": "formatting",
            "label": "Formatting & Parser Safety",
            "weight": 0.20,
            "score": fmt_score,
            "weighted_points": round(fmt_score * 0.20, 2),
            "evidence": fmt_evidence,
            "recommendations": fmt_recs,
        },
        {
            "key": "completeness",
            "label": "Section & Header Completeness",
            "weight": 0.20,
            "score": sec_score,
            "weighted_points": round(sec_score * 0.20, 2),
            "evidence": sec_evidence,
            "recommendations": sec_recs,
        },
        {
            "key": "keywords",
            "label": "Keyword & Evidence Density",
            "weight": 0.25,
            "score": kw_score,
            "weighted_points": round(kw_score * 0.25, 2),
            "evidence": kw_evidence,
            "recommendations": kw_recs,
        },
        {
            "key": "impact",
            "label": "Measurable Impact & Action Verbs",
            "weight": 0.25,
            "score": imp_score,
            "weighted_points": round(imp_score * 0.25, 2),
            "evidence": imp_evidence,
            "recommendations": imp_recs,
        },
        {
            "key": "readability",
            "label": "Readability & Conciseness",
            "weight": 0.10,
            "score": read_score,
            "weighted_points": round(read_score * 0.10, 2),
            "evidence": read_evidence,
            "recommendations": read_recs,
        },
    ]

    overall_score = round(sum(d["weighted_points"] for d in dimensions), 1)
    grade = _grade_from_score(overall_score)

    action_plan: list[dict[str, Any]] = []
    for dim in sorted(dimensions, key=lambda item: item["score"]):
        for rec in dim["recommendations"]:
            potential_gain = round((100.0 - dim["score"]) * dim["weight"] * 0.6, 1)
            action_plan.append(
                {
                    "dimension": dim["label"],
                    "priority": "high" if dim["score"] < 65 else "medium",
                    "recommendation": rec,
                    "estimated_score_uplift": max(1.0, potential_gain),
                }
            )

    return {
        "overall_score": overall_score,
        "grade": grade,
        "pass_likelihood": (
            "High (>80% ATS pass likelihood)"
            if overall_score >= 78
            else "Moderate (55-80% ATS pass likelihood)"
            if overall_score >= 60
            else "At Risk (<55% ATS pass likelihood)"
        ),
        "dimensions": dimensions,
        "action_plan": action_plan[:8],
    }
