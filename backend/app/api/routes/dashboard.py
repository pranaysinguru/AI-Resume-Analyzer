"""Career Intelligence Dashboard route aggregating live persisted analytics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import CareerTwinSnapshot, InterviewSession, JobMatchRecord, ResumeVersion
from app.services.career_predictor import predict_career_roles

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def get_dashboard_overview(resume_id: int | None = None, db: Session = Depends(get_db)) -> dict[str, object]:
    """Return live Career Intelligence Dashboard metrics computed purely from persisted records."""
    all_versions = db.query(ResumeVersion).order_by(asc(ResumeVersion.created_at), asc(ResumeVersion.id)).all()
    if not all_versions:
        return {
            "has_data": False,
            "summary_metrics": {
                "total_versions": 0,
                "latest_ats_score": 0.0,
                "best_ats_score": 0.0,
                "total_job_matches": 0,
                "avg_job_match_score": 0.0,
                "interview_sessions_count": 0,
                "career_twin_health": 0.0,
            },
            "active_resume": None,
            "ats_trend": [],
            "skill_distribution": [],
            "recent_job_matches": [],
            "top_career_recommendations": [],
            "priority_recommendations": [],
        }

    active = db.get(ResumeVersion, resume_id) if resume_id is not None else all_versions[-1]
    if active is None:
        active = all_versions[-1]

    job_matches = (
        db.query(JobMatchRecord)
        .order_by(desc(JobMatchRecord.created_at), desc(JobMatchRecord.id))
        .limit(10)
        .all()
    )
    total_matches = db.query(JobMatchRecord).count()
    interview_count = db.query(InterviewSession).count()

    latest_twin = (
        db.query(CareerTwinSnapshot)
        .filter(CareerTwinSnapshot.resume_version_id == active.id)
        .order_by(desc(CareerTwinSnapshot.created_at), desc(CareerTwinSnapshot.id))
        .first()
    )

    ats_scores = [float(v.ats_score) for v in all_versions]
    avg_match = (
        round(sum(float(m.overall_score) for m in job_matches) / len(job_matches), 1)
        if job_matches
        else 0.0
    )

    by_category = active.parsed_data.get("skills", {}).get("by_category", {})
    evidenced_set = set(active.parsed_data.get("skills", {}).get("evidenced_skills", []))
    skill_distribution = [
        {
            "category": cat,
            "total": len(skills),
            "evidenced": sum(1 for s in skills if s in evidenced_set),
        }
        for cat, skills in by_category.items()
    ]

    ats_trend = [
        {
            "id": v.id,
            "label": v.version_label,
            "version_number": v.version_number,
            "ats_score": v.ats_score,
            "grade": v.quality_grade,
            "word_count": v.word_count,
            "created_at": v.created_at,
        }
        for v in all_versions
    ]

    if latest_twin:
        twin_health = float(latest_twin.twin_data.get("twin_health_score", 0.0))
        career_recs = latest_twin.twin_data.get("career_predictions", [])
    else:
        twin_health = 0.0
        career_recs = predict_career_roles(
            {**active.parsed_data, "sanitized_text": active.sanitized_text}
        )["recommendations"]

    return {
        "has_data": True,
        "summary_metrics": {
            "total_versions": len(all_versions),
            "latest_ats_score": float(active.ats_score),
            "best_ats_score": max(ats_scores),
            "total_job_matches": total_matches,
            "avg_job_match_score": avg_match,
            "interview_sessions_count": interview_count,
            "career_twin_health": twin_health,
        },
        "active_resume": {
            "id": active.id,
            "profile_id": active.profile_id,
            "version_label": active.version_label,
            "filename": active.filename,
            "ats_score": active.ats_score,
            "quality_grade": active.quality_grade,
            "technical_skills_count": len(active.parsed_data.get("skills", {}).get("technical_skills", [])),
            "evidenced_skills_count": len(evidenced_set),
            "bullet_stats": active.parsed_data.get("bullet_stats", {}),
            "ats_dimensions": active.ats_report.get("dimensions", []),
        },
        "ats_trend": ats_trend,
        "skill_distribution": skill_distribution,
        "recent_job_matches": [
            {
                "id": m.id,
                "job_title": m.job_title,
                "company": m.company,
                "overall_score": m.overall_score,
                "skill_coverage": m.skill_coverage,
                "semantic_similarity": m.semantic_similarity,
                "created_at": m.created_at,
            }
            for m in job_matches
        ],
        "top_career_recommendations": career_recs[:4],
        "priority_recommendations": active.ats_report.get("action_plan", [])[:5],
    }
