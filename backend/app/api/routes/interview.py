"""Personalized AI Interview Simulator routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import InterviewSession, ResumeVersion
from app.schemas.contracts import InterviewGenerateRequest
from app.services.interview_sim import generate_interview_questions

router = APIRouter(prefix="/interview", tags=["AI Interview Simulator"])


@router.post("/generate")
def create_interview_session(payload: InterviewGenerateRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    """Generate personalized technical, project, behavioral, and HR interview questions."""
    row = db.get(ResumeVersion, payload.resume_version_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found.")

    parsed = {**row.parsed_data, "sanitized_text": row.sanitized_text}
    generated = generate_interview_questions(
        parsed=parsed,
        target_role=payload.target_role,
        job_description=payload.job_description,
        difficulty=payload.difficulty,
    )

    session = InterviewSession(
        resume_version_id=row.id,
        target_role=payload.target_role,
        questions_data=generated,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "resume_version_id": row.id,
        "created_at": session.created_at,
        **generated,
    }


@router.get("/history/{resume_id}")
def list_interview_sessions(resume_id: int, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    """Retrieve previously generated interview sessions for a resume version."""
    rows = (
        db.query(InterviewSession)
        .filter(InterviewSession.resume_version_id == resume_id)
        .order_by(desc(InterviewSession.created_at), desc(InterviewSession.id))
        .limit(10)
        .all()
    )
    return [
        {
            "session_id": r.id,
            "resume_version_id": r.resume_version_id,
            "target_role": r.target_role,
            "created_at": r.created_at,
            **r.questions_data,
        }
        for r in rows
    ]
