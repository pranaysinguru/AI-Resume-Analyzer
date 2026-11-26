"""SQLAlchemy ORM models for ResumeX AI."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CandidateProfile(Base):
    """Logical candidate workspace grouping resume versions and Career Twin."""

    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    display_label: Mapped[str] = mapped_column(String(120), nullable=False)
    target_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    versions: Mapped[list[ResumeVersion]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="ResumeVersion.version_number",
    )
    career_twins: Mapped[list[CareerTwinSnapshot]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class ResumeVersion(Base):
    """Persisted resume analysis snapshot with explainable ATS and recruiter audits."""

    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    version_label: Mapped[str] = mapped_column(String(120), default="v1")
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    page_count: Mapped[int] = mapped_column(Integer, default=1)
    sanitized_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    ats_score: Mapped[float] = mapped_column(Float, default=0.0)
    ats_report: Mapped[dict] = mapped_column(JSON, nullable=False)
    recruiter_audit: Mapped[dict] = mapped_column(JSON, nullable=False)
    quality_grade: Mapped[str] = mapped_column(String(8), default="B")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    profile: Mapped[CandidateProfile] = relationship(back_populates="versions")
    job_matches: Mapped[list[JobMatchRecord]] = relationship(
        back_populates="resume_version",
        cascade="all, delete-orphan",
    )
    interview_sessions: Mapped[list[InterviewSession]] = relationship(
        back_populates="resume_version",
        cascade="all, delete-orphan",
    )


class JobMatchRecord(Base):
    """Stored semantic and skill-gap comparison against a job description."""

    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True
    )
    job_title: Mapped[str] = mapped_column(String(160), nullable=False)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    job_description_hash: Mapped[str] = mapped_column(String(64), index=True)
    job_description_excerpt: Mapped[str] = mapped_column(String(500), nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    skill_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    experience_alignment: Mapped[float] = mapped_column(Float, nullable=False)
    result_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    resume_version: Mapped[ResumeVersion] = relationship(back_populates="job_matches")


class CareerTwinSnapshot(Base):
    """Evidence-backed Career Twin representation generated from resume versions."""

    __tablename__ = "career_twins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True
    )
    resume_version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True
    )
    twin_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    profile: Mapped[CandidateProfile] = relationship(back_populates="career_twins")


class InterviewSession(Base):
    """Generated tailored interview questions grounded in resume evidence and target JD."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_version_id: Mapped[int] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True
    )
    target_role: Mapped[str] = mapped_column(String(160), nullable=False)
    questions_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    resume_version: Mapped[ResumeVersion] = relationship(back_populates="interview_sessions")
