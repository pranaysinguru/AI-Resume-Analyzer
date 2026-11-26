"""Unit tests for file validation, PII masking, zero-fabrication enhancer, and NLP parsing."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.privacy import redact_pii, validate_resume_upload
from app.nlp.parser import parse_resume_bytes
from app.services.enhancer import enhance_bullet
from tests.conftest import build_sample_docx_bytes, build_sample_pdf_bytes


def test_invalid_extension_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_resume_upload("malware.exe", b"MZ123456")
    assert exc.value.status_code == 415


def test_fake_pdf_header_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_resume_upload("fake.pdf", b"NOT_A_REAL_PDF_FILE")
    assert exc.value.status_code == 400


def test_empty_file_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_resume_upload("empty.docx", b"")
    assert exc.value.status_code == 400


def test_pii_redaction_masks_email_and_phone():
    raw = "Reach me at pranay.dev@gmail.com or +1 (415) 555-8192."
    masked = redact_pii(raw)
    assert "pranay.dev@gmail.com" not in masked
    assert "555-8192" not in masked
    assert "pr***@gmail.com" in masked
    assert "***-***-8192" in masked


def test_pdf_and_docx_parsing_extract_structured_intelligence():
    docx_parsed = parse_resume_bytes(build_sample_docx_bytes(strong=True), ".docx")
    pdf_parsed = parse_resume_bytes(build_sample_pdf_bytes(), ".pdf")

    assert "alex.mercer@example.com" not in docx_parsed["sanitized_text"]
    assert docx_parsed["contact"]["email_masked"] == "al***@example.com"
    assert "Python" in docx_parsed["skills"]["all_skills"]
    assert "FastAPI" in docx_parsed["skills"]["evidenced_skills"]
    assert docx_parsed["bullet_stats"]["quantified"] >= 2

    assert "PyTorch" in pdf_parsed["skills"]["all_skills"]
    assert pdf_parsed["layout"]["page_count"] == 1
    assert pdf_parsed["estimated_years_experience"] >= 2.0


def test_enhancer_never_fabricates_metrics():
    weak = "Responsible for building API endpoints with FastAPI."
    res = enhance_bullet(weak, target_role="Backend Engineer")
    assert res["fabrication_free"] is True
    assert res["has_verified_metric"] is False
    assert "[insert real metric" in res["enhanced"]
    assert not res["enhanced"].lower().startswith("responsible for")

    strong = "Reduced FastAPI latency by 35% using Redis caching."
    res_strong = enhance_bullet(strong)
    assert res_strong["has_verified_metric"] is True
    assert "35%" in res_strong["enhanced"]
    assert "[insert real metric" not in res_strong["enhanced"]
