"""Personalized AI Interview Simulator grounded in resume evidence and target JD."""

from __future__ import annotations

from typing import Any

from app.nlp.skill_taxonomy import extract_skills


def generate_interview_questions(
    parsed: dict[str, Any],
    target_role: str,
    job_description: str | None = None,
    difficulty: str = "mixed",
) -> dict[str, Any]:
    """Generate tailored technical, project-based, behavioral, and HR questions."""
    evidenced = parsed["skills"]["evidenced_skills"]
    unverified = parsed["skills"]["unverified_skills"]
    technical = [s["skill"] for s in parsed["skills"]["technical_skills"]]
    projects = parsed["project_entries"]
    experiences = parsed["experience_entries"]
    bullets = parsed["bullets"]

    jd_skills = extract_skills(job_description)["all_skills"] if job_description else []
    missing_from_jd = [s for s in jd_skills if s not in set(parsed["skills"]["all_skills"])]

    questions: list[dict[str, Any]] = []

    def _diff(idx: int) -> str:
        if difficulty != "mixed":
            return difficulty
        return ("junior", "mid", "senior")[idx % 3]

    # 1. Project-Based Deep Dives (grounded in actual projects or experience entries)
    project_sources = projects[:2] or experiences[:2]
    for idx, entry in enumerate(project_sources):
        title = entry["title_line"]
        highlight = entry["highlights"][0] if entry["highlights"] else title
        questions.append(
            {
                "id": f"proj-{idx + 1}",
                "category": "Project Deep Dive",
                "difficulty": _diff(idx + 1),
                "question": (
                    f"Walk me through the architecture of '{title}'. Specifically, regarding '{highlight[:120]}', "
                    f"what technical trade-offs did you make and what failed or bottlenecked first under load or edge cases?"
                ),
                "grounded_in": title,
                "what_interviewers_look_for": [
                    "Clear system boundaries, data flow, and why alternatives were rejected.",
                    "Honest discussion of bottlenecks, testing, and measurable outcomes.",
                ],
                "answering_framework": "Context -> Architecture & Alternatives -> Bottleneck/Bug -> Verified Result.",
            }
        )

    if bullets:
        no_metric_bullet = next((b for b in bullets if not b["has_metric"]), bullets[0])
        questions.append(
            {
                "id": "proj-metric-probe",
                "category": "Project Deep Dive",
                "difficulty": "mid",
                "question": (
                    f"On your resume you wrote: \"{no_metric_bullet['text']}\". How did you validate that your implementation "
                    f"actually worked well—what metrics, benchmarks, or test cases did you measure?"
                ),
                "grounded_in": no_metric_bullet["text"],
                "what_interviewers_look_for": [
                    "Ability to define concrete evaluation criteria (latency, accuracy, error rate, test coverage).",
                    "Ownership of quality beyond just writing code.",
                ],
                "answering_framework": "Baseline -> Validation Method -> Measured Delta -> Lesson Learned.",
            }
        )

    # 2. Technical Questions (evidenced stack + unverified skills probe + JD gap check)
    focus_tech = (evidenced[:3] or technical[:3] or ["Python", "SQL", "System Design"])
    for idx, skill in enumerate(focus_tech[:3]):
        questions.append(
            {
                "id": f"tech-{idx + 1}",
                "category": "Technical",
                "difficulty": _diff(idx),
                "question": (
                    f"You list {skill} on your resume. For a {target_role} role, describe a non-trivial production or debugging "
                    f"problem you solved with {skill}, including performance, concurrency, or schema/model trade-offs."
                ),
                "grounded_in": f"Resume skill: {skill}",
                "what_interviewers_look_for": [
                    f"Depth in {skill} internals rather than surface-level tutorial usage.",
                    "Debugging methodology and awareness of failure modes.",
                ],
                "answering_framework": "Problem Symptom -> Root Cause -> Implementation Fix -> Prevention/Tests.",
            }
        )

    if unverified:
        probe_skill = unverified[0]
        questions.append(
            {
                "id": "tech-unverified-probe",
                "category": "Technical",
                "difficulty": "mid",
                "question": (
                    f"I noticed {probe_skill} is listed under your Skills section, though it wasn't detailed in your projects. "
                    f"Where have you used {probe_skill} hands-on, and how would you apply it in this {target_role} position?"
                ),
                "grounded_in": f"Unverified skill in Skills section: {probe_skill}",
                "what_interviewers_look_for": [
                    "Honesty about proficiency level (production vs. coursework/exploration).",
                    "Accurate mental model of when and why to use the tool.",
                ],
                "answering_framework": "Honest Scope -> Concrete Example -> How You Would Ramp Up.",
            }
        )

    if missing_from_jd:
        gap_skill = missing_from_jd[0]
        questions.append(
            {
                "id": "tech-jd-gap",
                "category": "Technical",
                "difficulty": "mid",
                "question": (
                    f"This {target_role} role relies on {gap_skill}, which isn't explicitly shown on your resume. "
                    f"Which overlapping concepts from your current stack ({', '.join(focus_tech[:2])}) transfer directly, and how would you bridge {gap_skill} in your first 30 days?"
                ),
                "grounded_in": f"Target JD requirement: {gap_skill}",
                "what_interviewers_look_for": [
                    "Transferable engineering fundamentals rather than bluffing.",
                    "Structured self-learning and onboarding speed.",
                ],
                "answering_framework": "Acknowledge Gap -> Map Analogous Experience -> 30-Day Execution Plan.",
            }
        )

    # 3. Behavioral Questions (STAR)
    exp_anchor = experiences[0]["title_line"] if experiences else (projects[0]["title_line"] if projects else "your recent team project")
    questions.extend(
        [
            {
                "id": "behav-1",
                "category": "Behavioral",
                "difficulty": "mid",
                "question": (
                    f"Tell me about a time during '{exp_anchor}' when requirements changed late or you disagreed with a technical approach. "
                    f"How did you align stakeholders or teammates and still ship?"
                ),
                "grounded_in": exp_anchor,
                "what_interviewers_look_for": [
                    "Data-driven persuasion, ego-free collaboration, and pragmatic delivery.",
                ],
                "answering_framework": "Situation -> Task -> Action (your specific influence) -> Result.",
            },
            {
                "id": "behav-2",
                "category": "Behavioral",
                "difficulty": _diff(2),
                "question": (
                    "Describe a bug, outage, or model/data quality issue you missed before shipping. "
                    "How did you detect it, communicate the impact, and harden the system afterward?"
                ),
                "grounded_in": "Engineering ownership & post-mortem maturity",
                "what_interviewers_look_for": [
                    "Accountability without blaming others and systemic prevention (tests, alerts, validation).",
                ],
                "answering_framework": "Incident -> Mitigation -> Root Cause -> Safeguard Added.",
            },
        ]
    )

    # 4. HR / Career Alignment Questions
    questions.extend(
        [
            {
                "id": "hr-1",
                "category": "HR",
                "difficulty": "junior",
                "question": (
                    f"Based on your background ({len(technical)} technical skills, {len(projects)} highlighted projects), "
                    f"why are you targeting a {target_role} role now, and what kind of problems energize you most?"
                ),
                "grounded_in": "Career trajectory & role motivation",
                "what_interviewers_look_for": [
                    "Authentic connection between past projects and the target role's day-to-day reality.",
                ],
                "answering_framework": "Past Proof -> Present Motivation -> Value You Bring to the Team.",
            },
            {
                "id": "hr-2",
                "category": "HR",
                "difficulty": "junior",
                "question": (
                    "What feedback have you received from a mentor, manager, or teammate in the past year, "
                    "and what concrete habit did you change because of it?"
                ),
                "grounded_in": "Coachability & growth mindset",
                "what_interviewers_look_for": [
                    "Self-awareness and concrete behavioral change rather than disguised humble-brags.",
                ],
                "answering_framework": "Specific Feedback -> Actionable Habit Change -> Observable Outcome.",
            },
        ]
    )

    counts: dict[str, int] = {}
    for q in questions:
        cat = str(q["category"])
        counts[cat] = counts.get(cat, 0) + 1

    return {
        "target_role": target_role,
        "difficulty_mode": difficulty,
        "total_questions": len(questions),
        "category_breakdown": counts,
        "questions": questions,
    }
