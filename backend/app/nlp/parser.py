"""PDF/DOCX resume parser, section segmenter, and quality diagnostics engine."""

from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Any

import docx
import pymupdf

from app.core.privacy import (
    EMAIL_RE,
    GITHUB_RE,
    LINKEDIN_RE,
    PHONE_RE,
    mask_email,
    mask_phone,
    redact_pii,
)
from app.nlp.embeddings import get_spacy_nlp
from app.nlp.skill_taxonomy import extract_skills

SECTION_PATTERNS: dict[str, tuple[str, ...]] = {
    "summary": (
        "summary",
        "professional summary",
        "profile",
        "career objective",
        "objective",
        "about me",
    ),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "internships",
        "internship",
    ),
    "projects": (
        "projects",
        "key projects",
        "selected projects",
        "academic projects",
        "personal projects",
    ),
    "education": (
        "education",
        "academic background",
        "qualifications",
        "academic qualifications",
    ),
    "skills": (
        "skills",
        "technical skills",
        "core competencies",
        "technologies",
        "tech stack",
        "tools & technologies",
    ),
    "certifications": (
        "certifications",
        "certificates",
        "licenses",
        "licenses & certifications",
        "courses",
    ),
    "achievements": (
        "achievements",
        "awards",
        "honors",
        "publications",
        "accomplishments",
        "extracurricular",
    ),
}

STRONG_ACTION_VERBS = {
    "accelerated", "architected", "automated", "built", "championed", "configured",
    "consolidated", "constructed", "created", "decreased", "delivered", "deployed",
    "designed", "developed", "devised", "diagnosed", "drove", "eliminated",
    "engineered", "enhanced", "established", "evaluated", "executed", "expanded",
    "formulated", "generated", "implemented", "improved", "increased", "initiated",
    "integrated", "launched", "led", "mentored", "migrated", "modeled",
    "modernized", "optimized", "orchestrated", "overhauled", "pioneered", "predicted",
    "produced", "programmed", "rearchitected", "reduced", "refactored", "redesigned",
    "resolved", "scaled", "secured", "shipped", "simplified", "spearheaded",
    "standardized", "streamlined", "tested", "trained", "transformed", "tuned",
    "validated",
}

WEAK_PHRASES = (
    "responsible for",
    "duties included",
    "worked on",
    "helped with",
    "assisted with",
    "assisted in",
    "tasked with",
    "involved in",
    "handled various",
    "various tasks",
    "hardworking",
    "team player",
    "detail oriented",
    "go-getter",
)

METRIC_RE = re.compile(
    r"(\b\d+(?:\.\d+)?%|\$\s?\d+(?:[.,]\d+)?[kKmMbB]?|\b\d+(?:\.\d+)?x\b|\b\d+(?:,\d{3})+\+?|\b\d+(?:\.\d+)?\s*(?:ms|sec|seconds|minutes|hrs|hours|days|users|requests|rps|qps|records|rows|pipelines|models|endpoints|clients|customers|tickets|bugs)\b)",
    re.IGNORECASE,
)

DATE_RANGE_RE = re.compile(
    r"(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+)?(20\d{2}|19\d{2})\s*[-–—to]+\s*(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+)?(20\d{2}|19\d{2}|Present|Current|Now)",
    re.IGNORECASE,
)

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _extract_pdf(content: bytes) -> dict[str, Any]:
    doc = pymupdf.open(stream=content, filetype="pdf")
    try:
        pages_text: list[str] = []
        image_count = 0
        table_count = 0
        multi_column_pages = 0
        font_sizes: list[float] = []

        for page in doc:
            page_text = page.get_text("text") or ""
            pages_text.append(page_text)
            image_count += len(page.get_images(full=True))

            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    table_count += len(tabs.tables)
            except Exception:
                pass

            blocks = page.get_text("dict").get("blocks", [])
            x_starts = []
            page_width = page.rect.width or 600.0
            for blk in blocks:
                if blk.get("type") == 0 and blk.get("lines"):
                    x0 = blk["bbox"][0]
                    x_starts.append(x0 / page_width)
                    for line in blk["lines"]:
                        for span in line.get("spans", []):
                            if span.get("size"):
                                font_sizes.append(round(float(span["size"]), 1))

            left_blocks = sum(1 for x in x_starts if x < 0.38)
            right_blocks = sum(1 for x in x_starts if x > 0.48)
            if left_blocks >= 3 and right_blocks >= 3:
                multi_column_pages += 1

        raw_text = "\n".join(pages_text)
        return {
            "raw_text": raw_text,
            "page_count": len(doc),
            "image_count": image_count,
            "table_count": table_count,
            "multi_column_risk": multi_column_pages > 0,
            "distinct_font_sizes": len(set(font_sizes)),
        }
    finally:
        doc.close()


def _extract_docx(content: bytes) -> dict[str, Any]:
    document = docx.Document(io.BytesIO(content))
    lines: list[str] = []
    for para in document.paragraphs:
        if para.text.strip():
            lines.append(para.text.strip())

    table_count = len(document.tables)
    for table in document.tables:
        for row in table.rows:
            row_vals = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_vals:
                lines.append(" | ".join(dict.fromkeys(row_vals)))

    image_count = len(document.inline_shapes)
    raw_text = "\n".join(lines)
    estimated_pages = max(1, (len(raw_text.split()) + 420) // 450)
    return {
        "raw_text": raw_text,
        "page_count": estimated_pages,
        "image_count": image_count,
        "table_count": table_count,
        "multi_column_risk": table_count >= 2,
        "distinct_font_sizes": 3,
    }


def _normalize_heading(line: str) -> str | None:
    cleaned = re.sub(r"[:|\-–—•]+$", "", line.strip()).strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned or len(cleaned) > 45 or len(cleaned.split()) > 5:
        return None
    for section_key, aliases in SECTION_PATTERNS.items():
        if cleaned in aliases:
            return section_key
    return None


def _segment_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = _normalize_heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _extract_contact(header_lines: list[str], full_text: str) -> dict[str, Any]:
    email_match = EMAIL_RE.search(full_text)
    phone_match = PHONE_RE.search(full_text)
    linkedin_match = LINKEDIN_RE.search(full_text)
    github_match = GITHUB_RE.search(full_text)

    candidate_label = "Candidate Resume"
    for line in header_lines[:4]:
        if (
            not EMAIL_RE.search(line)
            and not PHONE_RE.search(line)
            and "http" not in line.lower()
            and 2 <= len(line.split()) <= 5
            and re.match(r"^[A-Za-z.\s'-]+$", line)
        ):
            parts = line.split()
            candidate_label = f"{parts[0]} {parts[-1][0]}." if len(parts) > 1 else parts[0]
            break

    return {
        "candidate_label": candidate_label,
        "has_email": bool(email_match),
        "email_masked": mask_email(email_match.group(0)) if email_match else None,
        "has_phone": bool(phone_match),
        "phone_masked": mask_phone(phone_match.group(0)) if phone_match else None,
        "has_linkedin": bool(linkedin_match),
        "linkedin_url": linkedin_match.group(0) if linkedin_match else None,
        "has_github": bool(github_match),
        "github_url": github_match.group(0) if github_match else None,
    }


def _analyze_bullets(sections: dict[str, list[str]]) -> list[dict[str, Any]]:
    bullets: list[dict[str, Any]] = []
    bullet_prefix_re = re.compile(r"^[•●▪◦\-*>]+\s*")
    target_sections = ("experience", "projects", "achievements")

    for sec in target_sections:
        lines = sections.get(sec, [])
        for line in lines:
            is_bullet = bool(bullet_prefix_re.match(line))
            clean = bullet_prefix_re.sub("", line).strip()
            words = clean.split()
            if len(words) < 5:
                continue
            if not is_bullet and len(words) < 8:
                continue
            if DATE_RANGE_RE.search(clean) and len(words) <= 9 and "|" in clean:
                continue

            first_word = re.sub(r"[^a-zA-Z]", "", words[0]).lower()
            metrics = METRIC_RE.findall(clean)
            weak_hits = [phrase for phrase in WEAK_PHRASES if phrase in clean.lower()]

            bullets.append(
                {
                    "section": sec,
                    "text": redact_pii(clean),
                    "word_count": len(words),
                    "action_verb": first_word,
                    "starts_with_strong_verb": first_word in STRONG_ACTION_VERBS,
                    "has_metric": len(metrics) > 0,
                    "metrics_found": metrics[:4],
                    "weak_phrases": weak_hits,
                }
            )
    return bullets


def _estimate_experience_years(text: str) -> float:
    now = datetime.now()
    total_months = 0
    seen_ranges: set[tuple[int, int]] = set()
    for match in DATE_RANGE_RE.finditer(text):
        m1_str, y1_str, m2_str, y2_str = match.groups()
        y1 = int(y1_str)
        m1 = MONTH_MAP.get((m1_str or "").lower(), 1)
        if y2_str.lower() in ("present", "current", "now"):
            y2, m2 = now.year, now.month
        else:
            y2 = int(y2_str)
            m2 = MONTH_MAP.get((m2_str or "").lower(), 12)
        if y2 < y1 or y1 < 1980 or y2 > now.year + 1:
            continue
        span = (y2 - y1) * 12 + (m2 - m1) + 1
        key = (y1 * 12 + m1, y2 * 12 + m2)
        if span > 0 and key not in seen_ranges:
            seen_ranges.add(key)
            total_months += min(span, 120)
    return round(total_months / 12.0, 1)


def _extract_entities_summary(text: str) -> dict[str, list[str]]:
    nlp = get_spacy_nlp()
    doc = nlp(text[:12000])
    orgs: list[str] = []
    locations: list[str] = []
    for ent in doc.ents:
        val = ent.text.strip()
        if len(val) < 2 or len(val) > 50:
            continue
        if ent.label_ == "ORG" and val not in orgs:
            orgs.append(val)
        elif ent.label_ == "GPE" and val not in locations:
            locations.append(val)
    return {
        "organizations": orgs[:12],
        "locations": locations[:6],
    }


def _extract_entries(lines: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    bullet_prefix_re = re.compile(r"^[•●▪◦\-*>]+\s*")

    for line in lines:
        is_bullet = bool(bullet_prefix_re.match(line))
        clean = bullet_prefix_re.sub("", line).strip()
        has_date = bool(DATE_RANGE_RE.search(clean))
        if not is_bullet and (has_date or ("|" in clean and len(clean.split()) <= 14)):
            if current:
                entries.append(current)
            current = {
                "title_line": redact_pii(clean),
                "highlights": [],
            }
        elif current is not None:
            current["highlights"].append(redact_pii(clean))
        else:
            current = {
                "title_line": redact_pii(clean),
                "highlights": [],
            }
    if current:
        entries.append(current)
    return entries[:12]


def parse_resume_bytes(content: bytes, extension: str) -> dict[str, Any]:
    """Parse PDF or DOCX bytes into structured, PII-safe resume intelligence."""
    if extension == ".pdf":
        raw_meta = _extract_pdf(content)
    elif extension == ".docx":
        raw_meta = _extract_docx(content)
    else:
        raise ValueError(f"Unsupported extension: {extension}")

    raw_text = raw_meta["raw_text"].strip()
    if len(raw_text.split()) < 20:
        raise ValueError(
            "Unable to extract sufficient readable text from this file. "
            "If this is a scanned/image-based PDF, please export a text-selectable PDF or DOCX."
        )

    sanitized_text = redact_pii(raw_text)
    sections = _segment_sections(raw_text)
    contact = _extract_contact(sections.get("header", []), raw_text)
    bullets = _analyze_bullets(sections)
    skills_full = extract_skills(sanitized_text)

    evidence_text = "\n".join(
        sections.get("experience", []) + sections.get("projects", []) + sections.get("achievements", [])
    )
    skills_evidenced = extract_skills(redact_pii(evidence_text)) if evidence_text.strip() else {
        "all_skills": [],
        "technical_skills": [],
        "soft_skills": [],
    }

    years_exp = _estimate_experience_years(
        "\n".join(sections.get("experience", [])) or sanitized_text
    )
    entities = _extract_entities_summary(sanitized_text)

    words = sanitized_text.split()
    word_count = len(words)
    sentences = [s for s in re.split(r"[.!?\n]+", sanitized_text) if len(s.strip().split()) >= 3]
    avg_sentence_words = round(word_count / max(1, len(sentences)), 1)

    present_sections = [
        sec
        for sec in ("summary", "experience", "projects", "education", "skills", "certifications", "achievements")
        if sections.get(sec)
    ]
    core_expected = ["summary", "experience", "projects", "education", "skills"]
    missing_sections = [sec for sec in core_expected if sec not in present_sections]

    quantified_bullets = [b for b in bullets if b["has_metric"]]
    strong_verb_bullets = [b for b in bullets if b["starts_with_strong_verb"]]
    weak_phrase_bullets = [b for b in bullets if b["weak_phrases"]]

    strengths: list[str] = []
    weaknesses: list[str] = []

    if len(skills_full["technical_skills"]) >= 8:
        strengths.append(f"Strong technical breadth with {len(skills_full['technical_skills'])} recognized skills.")
    else:
        weaknesses.append("Limited recognized technical skills; expand core tools and frameworks explicitly.")

    if bullets:
        metric_ratio = len(quantified_bullets) / len(bullets)
        if metric_ratio >= 0.45:
            strengths.append(f"{len(quantified_bullets)}/{len(bullets)} impact bullets include measurable metrics.")
        else:
            weaknesses.append(
                f"Only {len(quantified_bullets)} of {len(bullets)} bullets show quantifiable outcomes (%, $, latency, scale)."
            )
        verb_ratio = len(strong_verb_bullets) / len(bullets)
        if verb_ratio >= 0.6:
            strengths.append("Consistent use of strong action verbs at the start of accomplishments.")
        else:
            weaknesses.append("Several bullet points lack strong leading action verbs.")
    else:
        weaknesses.append("No structured bullet points detected under Experience or Projects.")

    if weak_phrase_bullets:
        weaknesses.append(
            f"Detected {len(weak_phrase_bullets)} bullets with passive/generic phrasing (e.g., 'responsible for', 'worked on')."
        )
    if missing_sections:
        weaknesses.append(f"Missing core resume sections: {', '.join(missing_sections)}.")
    else:
        strengths.append("All core ATS sections (Summary, Experience, Projects, Education, Skills) are present.")

    if contact["has_github"] or contact["has_linkedin"]:
        strengths.append("Includes verifiable professional profile links (GitHub/LinkedIn).")
    else:
        weaknesses.append("Missing LinkedIn or GitHub profile URLs for recruiter verification.")

    if raw_meta["multi_column_risk"]:
        weaknesses.append("Multi-column or table-heavy layout detected; some legacy ATS parsers may scramble reading order.")

    evidenced_set = set(skills_evidenced["all_skills"])
    skills_with_evidence = [
        {
            **item,
            "evidenced_in_experience_or_projects": item["skill"] in evidenced_set,
        }
        for item in skills_full["technical_skills"] + skills_full["soft_skills"]
    ]

    return {
        "sanitized_text": sanitized_text,
        "contact": contact,
        "layout": {
            "page_count": raw_meta["page_count"],
            "word_count": word_count,
            "avg_sentence_words": avg_sentence_words,
            "image_count": raw_meta["image_count"],
            "table_count": raw_meta["table_count"],
            "multi_column_risk": raw_meta["multi_column_risk"],
            "distinct_font_sizes": raw_meta["distinct_font_sizes"],
        },
        "sections_present": present_sections,
        "missing_sections": missing_sections,
        "section_contents": {
            sec: [redact_pii(line) for line in lines]
            for sec, lines in sections.items()
            if lines
        },
        "experience_entries": _extract_entries(sections.get("experience", [])),
        "project_entries": _extract_entries(sections.get("projects", [])),
        "education_entries": [redact_pii(l) for l in sections.get("education", [])[:8]],
        "certifications": [redact_pii(l) for l in sections.get("certifications", [])[:8]],
        "estimated_years_experience": years_exp,
        "entities": entities,
        "skills": {
            **skills_full,
            "evidenced_skills": sorted(evidenced_set),
            "unverified_skills": sorted(set(skills_full["all_skills"]) - evidenced_set),
            "detailed": skills_with_evidence,
        },
        "bullets": bullets,
        "bullet_stats": {
            "total": len(bullets),
            "quantified": len(quantified_bullets),
            "strong_verb": len(strong_verb_bullets),
            "weak_phrasing": len(weak_phrase_bullets),
        },
        "diagnostics": {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "quality_summary": (
                "Strong ATS-ready foundation"
                if len(strengths) >= len(weaknesses)
                else "High potential — addressing bullet metrics and structure will significantly raise ATS & recruiter scores."
            ),
        },
    }
