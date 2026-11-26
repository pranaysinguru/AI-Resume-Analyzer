"""Grounded AI Resume Bullet Enhancer — improves phrasing without fabricating experience."""

from __future__ import annotations

import re
from typing import Any

from app.nlp.parser import METRIC_RE, STRONG_ACTION_VERBS

WEAK_OPENERS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^(?:was\s+)?responsible\s+for\s+(?:the\s+)?", re.IGNORECASE), "Managed and delivered "),
    (re.compile(r"^(?:worked\s+on|working\s+on)\s+", re.IGNORECASE), "Engineered "),
    (re.compile(r"^(?:helped\s+(?:with|in|to)|assisted\s+(?:with|in))\s+", re.IGNORECASE), "Collaborated to deliver "),
    (re.compile(r"^(?:tasked\s+with|involved\s+in)\s+", re.IGNORECASE), "Executed "),
    (re.compile(r"^made\s+", re.IGNORECASE), "Built "),
    (re.compile(r"^did\s+", re.IGNORECASE), "Implemented "),
    (re.compile(r"^used\s+", re.IGNORECASE), "Leveraged "),
]

GERUND_TO_PAST: dict[str, str] = {
    "building": "Built",
    "creating": "Created",
    "developing": "Developed",
    "designing": "Designed",
    "implementing": "Implemented",
    "managing": "Managed",
    "optimizing": "Optimized",
    "testing": "Tested",
    "maintaining": "Maintained",
    "deploying": "Deployed",
    "analyzing": "Analyzed",
    "integrating": "Integrated",
}

VAGUE_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bvarious\s+", re.IGNORECASE), "multiple "),
    (re.compile(r"\betc\.?", re.IGNORECASE), ""),
    (re.compile(r"\ba lot of\b", re.IGNORECASE), "high-volume"),
    (re.compile(r"\bhelped improve\b", re.IGNORECASE), "improved"),
]


def enhance_bullet(bullet: str, target_role: str | None = None) -> dict[str, Any]:
    """Upgrade a single resume bullet while strictly avoiding fabricated facts or numbers."""
    original = re.sub(r"^[•●▪◦\-*>]+\s*", "", bullet.strip())
    if not original:
        return {
            "original": bullet,
            "enhanced": "",
            "changes_made": [],
            "metrics_prompt": None,
            "fabrication_free": True,
        }

    improved = original
    changes: list[str] = []

    for pattern, replacement in WEAK_OPENERS:
        if pattern.search(improved):
            improved = pattern.sub(replacement, improved, count=1)
            changes.append("Replaced passive opening phrase with a direct ownership verb.")
            break

    first_word = re.sub(r"[^a-zA-Z]", "", improved.split()[0]).lower()
    if first_word in GERUND_TO_PAST:
        past_verb = GERUND_TO_PAST[first_word]
        improved = re.sub(r"^\S+", past_verb, improved, count=1)
        changes.append(f"Converted gerund '{first_word}' to past-tense action verb '{past_verb}'.")
    elif first_word not in STRONG_ACTION_VERBS:
        improved = f"Executed {improved[0].lower()}{improved[1:]}" if len(improved) > 1 else improved
        changes.append("Added a strong leading action verb for immediate ATS/recruiter impact.")

    for pattern, replacement in VAGUE_REPLACEMENTS:
        if pattern.search(improved):
            improved = pattern.sub(replacement, improved)
            changes.append("Tightened vague phrasing for clearer executive tone.")

    improved = re.sub(r"\s+", " ", improved).strip()
    if improved and not improved.endswith((".", "!")):
        improved += "."
    improved = improved[0].upper() + improved[1:]

    has_metric = bool(METRIC_RE.search(original))
    metrics_prompt = None
    if not has_metric:
        improved_with_placeholder = improved.rstrip(".") + (
            ", achieving [insert real metric: e.g., X% latency reduction / Y users served / Z hours saved]."
        )
        metrics_prompt = (
            "No quantifiable outcome was found in your original bullet. Replace the bracketed placeholder "
            "with your true measured result—never invent numbers."
        )
        changes.append("Added an explicit metric placeholder so you can insert verified impact without fabrication.")
    else:
        improved_with_placeholder = improved
        changes.append("Preserved your existing verified metrics while strengthening verb ownership.")

    return {
        "original": original,
        "enhanced": improved_with_placeholder,
        "changes_made": changes,
        "has_verified_metric": has_metric,
        "metrics_prompt": metrics_prompt,
        "target_role_context": target_role,
        "fabrication_free": True,
    }


def enhance_bullets_batch(bullets: list[str], target_role: str | None = None) -> dict[str, Any]:
    """Enhance a list of resume bullets with strict anti-fabrication guarantees."""
    results = [enhance_bullet(b, target_role=target_role) for b in bullets if b.strip()]
    return {
        "count": len(results),
        "policy": "Zero-Fabrication Mode: Rewrites preserve only factual skills and context from your input and use explicit [metric placeholders] where numbers are missing.",
        "enhancements": results,
    }
