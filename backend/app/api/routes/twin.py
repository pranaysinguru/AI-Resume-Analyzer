"""Career Twin synthesis and retrieval routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import CareerTwinSnapshot, ResumeVersion
from app.schemas.contracts import CareerTwinRequest
from app.services.career_twin import build_career_twin

router = APIRouter(prefix="/twin", tags=["Career Twin"])


@router.post("/synthesize")
def synthesize_career_twin(payload: CareerTwinRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Generate or refresh an evidence-backed Career Twin snapshot with interests/role focus."""
    row = db.get(ResumeVersion, payload.resume_version_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    parsed = {**row.parsed_data, "sanitized_text": row.sanitized_text}
    twin = build_career_twin(
        parsed=parsed,
        ats_report=row.ats_report,
        career_interests=payload.career_interests,
        target_role=payload.target_role,
    )

    snapshot = CareerTwinSnapshot(
        profile_id=row.profile_id,
        resume_version_id=row.id,
        twin_data=twin,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "snapshot_id": snapshot.id,
        "resume_version_id": row.id,
        "created_at": snapshot.created_at,
        **twin,
    }


@router.get("/latest/{resume_id}")
def get_latest_twin(resume_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Fetch the latest Career Twin snapshot for a resume version."""
    row = db.get(ResumeVersion, resume_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    snapshot = (
        db.query(CareerTwinSnapshot)
        .filter(CareerTwinSnapshot.resume_version_id == resume_id)
        .order_by(desc(CareerTwinSnapshot.created_at), desc(CareerTwinSnapshot.id))
        .first()
    )
    if not snapshot:
        parsed = {**row.parsed_data, "sanitized_text": row.sanitized_text}
        twin = build_career_twin(parsed=parsed, ats_report=row.ats_report)
        return {"snapshot_id": None, "resume_version_id": row.id, **twin}

    return {
        "snapshot_id": snapshot.id,
        "resume_version_id": row.id,
        "created_at": snapshot.created_at,
        **snapshot.twin_data,
    }
