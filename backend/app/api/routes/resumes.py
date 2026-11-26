"""Resume upload, retrieval, deletion, and version comparison routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.privacy import validate_resume_upload
from app.models.entities import CandidateProfile, CareerTwinSnapshot, ResumeVersion
from app.nlp.parser import parse_resume_bytes
from app.schemas.contracts import ResumeDetailOut, ResumeSummaryOut, VersionCompareRequest
from app.services.ats_simulator import simulate_ats
from app.services.career_twin import build_career_twin
from app.services.recruiter_mode import audit_as_recruiter
from app.services.version_diff import compare_resume_versions

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeDetailOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    profile_id: int | None = Form(default=None),
    version_label: str | None = Form(default=None),
    target_role: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> ResumeVersion:
    """Validate, parse, analyze, and persist a PDF or DOCX resume without keeping raw PII files on disk."""
    raw_bytes = await file.read()
    validated = validate_resume_upload(file.filename, raw_bytes)

    try:
        parsed = parse_resume_bytes(validated.content, validated.extension)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse document structure: {exc}",
        ) from exc

    ats_report = simulate_ats(parsed)
    recruiter_audit = audit_as_recruiter(parsed, ats_report)

    profile: CandidateProfile | None = None
    if profile_id is not None:
        profile = db.get(CandidateProfile, profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate profile not found.")
    else:
        profile = CandidateProfile(
            display_label=parsed["contact"]["candidate_label"],
            target_role=target_role,
        )
        db.add(profile)
        db.flush()

    existing_count = (
        db.query(ResumeVersion).filter(ResumeVersion.profile_id == profile.id).count()
    )
    next_version = existing_count + 1
    label = (version_label or "").strip() or f"v{next_version} — {validated.filename[:40]}"

    resume_row = ResumeVersion(
        profile_id=profile.id,
        version_number=next_version,
        version_label=label,
        filename=validated.filename,
        file_type=validated.extension.lstrip("."),
        file_hash=validated.sha256,
        word_count=int(parsed["layout"]["word_count"]),
        page_count=int(parsed["layout"]["page_count"]),
        sanitized_text=parsed["sanitized_text"],
        parsed_data={k: v for k, v in parsed.items() if k != "sanitized_text"},
        ats_score=float(ats_report["overall_score"]),
        ats_report=ats_report,
        recruiter_audit=recruiter_audit,
        quality_grade=str(ats_report["grade"]),
    )
    db.add(resume_row)
    db.flush()

    twin_data = build_career_twin(
        parsed=parsed,
        ats_report=ats_report,
        career_interests=[target_role] if target_role else [],
        target_role=target_role,
    )
    db.add(
        CareerTwinSnapshot(
            profile_id=profile.id,
            resume_version_id=resume_row.id,
            twin_data=twin_data,
        )
    )
    db.commit()
    db.refresh(resume_row)
    return resume_row


@router.get("", response_model=list[ResumeSummaryOut])
def list_resumes(db: Session = Depends(get_db)) -> list[ResumeVersion]:
    """List all uploaded resume versions ordered newest first."""
    return db.query(ResumeVersion).order_by(desc(ResumeVersion.created_at), desc(ResumeVersion.id)).all()


@router.get("/{resume_id}", response_model=ResumeDetailOut)
def get_resume(resume_id: int, db: Session = Depends(get_db)) -> ResumeVersion:
    """Retrieve complete parsed intelligence, ATS score, and recruiter audit for a resume."""
    row = db.get(ResumeVersion, resume_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")
    return row


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
def delete_resume(resume_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Permanently delete a resume version and its dependent analyses."""
    row = db.get(ResumeVersion, resume_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")
    db.delete(row)
    db.commit()
    return {"deleted": True, "id": resume_id}


@router.post("/compare")
def compare_versions(payload: VersionCompareRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Compare two resume versions across ATS dimensions, skills, bullets, and optional JD compatibility."""
    base = db.get(ResumeVersion, payload.base_version_id)
    target = db.get(ResumeVersion, payload.target_version_id)
    if not base or not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both resume versions were not found.")

    base_parsed = {**base.parsed_data, "sanitized_text": base.sanitized_text}
    target_parsed = {**target.parsed_data, "sanitized_text": target.sanitized_text}
    base.parsed_data = base_parsed
    target.parsed_data = target_parsed

    return compare_resume_versions(base, target, job_description=payload.job_description)
