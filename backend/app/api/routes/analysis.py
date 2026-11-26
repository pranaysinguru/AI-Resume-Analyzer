"""ATS simulation, Recruiter Perspective audit, and Zero-Fabrication bullet enhancement routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import ResumeVersion
from app.schemas.contracts import EnhanceBulletsRequest
from app.services.enhancer import enhance_bullets_batch

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/{resume_id}/ats")
def get_ats_analysis(resume_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Return explainable ATS breakdown and prioritized recommendations."""
    row = db.get(ResumeVersion, resume_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")
    return row.ats_report


@router.get("/{resume_id}/recruiter")
def get_recruiter_audit(resume_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Return Recruiter Perspective Mode evaluation."""
    row = db.get(ResumeVersion, resume_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")
    return row.recruiter_audit


@router.post("/enhance-bullets")
def enhance_resume_bullets(payload: EnhanceBulletsRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Enhance provided bullets or weak bullets extracted from a stored resume without fabricating facts."""
    bullets_to_enhance = [b for b in payload.bullets if b.strip()]
    if not bullets_to_enhance and payload.resume_version_id is not None:
        row = db.get(ResumeVersion, payload.resume_version_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")
        raw_bullets = row.parsed_data.get("bullets", [])
        weak_first = [
            b["text"]
            for b in raw_bullets
            if not b.get("has_metric") or not b.get("starts_with_strong_verb") or b.get("weak_phrases")
        ]
        bullets_to_enhance = weak_first[:8] or [b["text"] for b in raw_bullets[:6]]

    if not bullets_to_enhance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one bullet point or a resume_version_id with extracted bullets.",
        )

    return enhance_bullets_batch(bullets_to_enhance, target_role=payload.target_role)
