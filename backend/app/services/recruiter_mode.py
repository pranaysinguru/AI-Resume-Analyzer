"""Recruiter Perspective Mode: critical hiring-manager & technical-screener audit."""

from __future__ import annotations

from typing import Any


def audit_as_recruiter(parsed: dict[str, Any], ats_report: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the resume through a critical 7-second + deep-scan recruiter lens."""
    skills = parsed["skills"]
    bullets = parsed["bullets"]
    bullet_stats = parsed["bullet_stats"]
    contact = parsed["contact"]
    years = float(parsed["estimated_years_experience"])

    top_evidenced = skills["evidenced_skills"][:6]
    unverified = skills["unverified_skills"]

    red_flags: list[dict[str, Any]] = []
    concerns: list[str] = []

    if unverified:
        red_flags.append(
            {
                "category": "Unverified Skills (Skill Inflation Risk)",
                "severity": "high" if len(unverified) >= 4 else "medium",
                "detail": (
                    f"{len(unverified)} skill(s) appear in your Skills list without supporting bullets in Experience or Projects: "
                    f"{', '.join(unverified[:6])}."
                ),
                "fix": "Either weave these tools into specific project/work bullets or remove peripheral tools you cannot defend in an interview.",
            }
        )

    weak_bullets = [b for b in bullets if not b["has_metric"] or b["weak_phrases"]]
    if bullets and len(weak_bullets) > len(bullets) * 0.5:
        red_flags.append(
            {
                "category": "Missing Outcome Evidence",
                "severity": "high",
                "detail": (
                    f"{len(weak_bullets)} of {len(bullets)} bullets describe responsibilities or activities without measurable impact."
                ),
                "fix": "Recruiters scan for scale and before/after deltas (e.g., latency reduction, adoption, accuracy, revenue).",
            }
        )
    elif not bullets:
        red_flags.append(
            {
                "category": "Unstructured Narrative Blocks",
                "severity": "high",
                "detail": "No clear accomplishment bullets were detected under Experience or Projects.",
                "fix": "Convert dense prose into scannable 1-2 line impact bullets.",
            }
        )

    if not contact["has_github"] and not contact["has_linkedin"]:
        red_flags.append(
            {
                "category": "Missing External Proof",
                "severity": "medium",
                "detail": "No GitHub or LinkedIn profile link detected for quick code/background verification.",
                "fix": "Add live GitHub and LinkedIn links in the header.",
            }
        )

    if "experience" not in parsed["sections_present"] and len(parsed["project_entries"]) < 2:
        red_flags.append(
            {
                "category": "Thin Hands-On Execution Signal",
                "severity": "high",
                "detail": "Neither work experience nor multiple detailed projects provide clear production-readiness proof.",
                "fix": "Highlight 2-3 substantive engineering projects with architecture choices, tests, and deployment details.",
            }
        )

    if parsed["layout"]["multi_column_risk"]:
        concerns.append("Multi-column formatting slows down linear 7-second eye tracking and risks ATS text reordering.")
    if "summary" not in parsed["sections_present"]:
        concerns.append("No executive summary at the top—recruiters must infer your target role manually.")
    if bullet_stats["weak_phrasing"] > 0:
        concerns.append("Passive phrases like 'responsible for' or 'worked on' dilute ownership.")

    unclear_bullets = [
        {
            "original": b["text"],
            "reason": (
                "Contains passive phrasing and lacks metrics"
                if b["weak_phrases"] and not b["has_metric"]
                else "No measurable result or scale indicator"
                if not b["has_metric"]
                else "Uses passive opening phrasing"
            ),
        }
        for b in weak_bullets[:5]
    ]

    overall_ats = float(ats_report["overall_score"])
    if overall_ats >= 78 and len([rf for rf in red_flags if rf["severity"] == "high"]) == 0:
        verdict = "Strong Shortlist"
        verdict_note = "Clear technical evidence, strong scannability, and verifiable outcomes."
    elif overall_ats >= 58:
        verdict = "Borderline — Needs Evidence Polish"
        verdict_note = "Solid underlying stack, but unclear metrics or unverified skills may lose to stronger applicants."
    else:
        verdict = "Likely Screened Out Early"
        verdict_note = "Missing core sections or low measurable impact limits recruiter confidence during a quick scan."

    return {
        "seven_second_scan": {
            "inferred_experience_years": years,
            "top_evidenced_skills": top_evidenced,
            "projects_detected": len(parsed["project_entries"]),
            "experience_roles_detected": len(parsed["experience_entries"]),
            "summary_present": "summary" in parsed["sections_present"],
        },
        "hiring_manager_verdict": verdict,
        "verdict_reasoning": verdict_note,
        "red_flags": red_flags,
        "concerns": concerns,
        "unclear_bullets": unclear_bullets,
        "recruiter_strength_signals": parsed["diagnostics"]["strengths"],
    }
