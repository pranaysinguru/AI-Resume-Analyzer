"""Job Matching, Skill Gap Intelligence, and Career Prediction routes."""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import JobMatchRecord, ResumeVersion
from app.schemas.contracts import CareerPredictRequest, JobMatchRequest, SkillGapRequest
from app.services.career_predictor import predict_career_roles
from app.services.job_matcher import match_resume_to_job
from app.services.skill_roadmap import analyze_skill_gaps

router = APIRouter(prefix="/matching", tags=["Job Matching & Career Intelligence"])


def _hydrated_parsed(row: ResumeVersion) -> dict:
    return {**row.parsed_data, "sanitized_text": row.sanitized_text}


@router.post("/job-match")
def run_job_match(payload: JobMatchRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Compare a resume against a target job description using hybrid NLP and semantic similarity."""
    row = db.get(ResumeVersion, payload.resume_version_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    parsed = _hydrated_parsed(row)
    result = match_resume_to_job(parsed, payload.job_title, payload.job_description)

    jd_hash = hashlib.sha256(payload.job_description.encode("utf-8")).hexdigest()
    breakdown = result["score_breakdown"]
    record = JobMatchRecord(
        resume_version_id=row.id,
        job_title=payload.job_title,
        company=payload.company,
        job_description_hash=jd_hash,
        job_description_excerpt=payload.job_description.strip()[:480],
        overall_score=float(result["overall_match_score"]),
        semantic_similarity=float(breakdown["semantic_similarity"]["score"]),
        skill_coverage=float(breakdown["skill_coverage"]["score"]),
        experience_alignment=float(breakdown["experience_alignment"]["score"]),
        result_data=result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "match_id": record.id,
        "resume_version_id": row.id,
        "company": payload.company,
        "created_at": record.created_at,
        **result,
    }


@router.get("/history")
def list_job_matches(resume_version_id: int | None = None, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    """List persisted job match evaluations."""
    query = db.query(JobMatchRecord)
    if resume_version_id is not None:
        query = query.filter(JobMatchRecord.resume_version_id == resume_version_id)
    rows = query.order_by(desc(JobMatchRecord.created_at), desc(JobMatchRecord.id)).limit(30).all()
    return [
        {
            "id": r.id,
            "resume_version_id": r.resume_version_id,
            "job_title": r.job_title,
            "company": r.company,
            "overall_score": r.overall_score,
            "semantic_similarity": r.semantic_similarity,
            "skill_coverage": r.skill_coverage,
            "experience_alignment": r.experience_alignment,
            "matched_skills": r.result_data.get("matched_skills", []),
            "missing_skills": r.result_data.get("missing_skills", []),
            "created_at": r.created_at,
        }
        for r in rows
    ]


@router.post("/skill-gaps")
def run_skill_gap_analysis(payload: SkillGapRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Identify missing technical/soft skills and build a personalized learning roadmap."""
    row = db.get(ResumeVersion, payload.resume_version_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    return analyze_skill_gaps(
        parsed=_hydrated_parsed(row),
        target_role=payload.target_role,
        job_description=payload.job_description,
    )


@router.post("/career-predict")
def run_career_prediction(payload: CareerPredictRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Predict best-fit career roles with explainable evidence reasoning."""
    row = db.get(ResumeVersion, payload.resume_version_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    return predict_career_roles(
        parsed=_hydrated_parsed(row),
        career_interests=payload.career_interests,
    )
