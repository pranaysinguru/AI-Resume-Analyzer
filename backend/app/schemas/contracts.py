"""Pydantic v2 API contracts for ResumeX AI."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ResumeSummaryOut(BaseModel):
    id: int
    profile_id: int
    version_number: int
    version_label: str
    filename: str
    file_type: str
    word_count: int
    page_count: int
    ats_score: float
    quality_grade: str
    created_at: datetime


class ResumeDetailOut(ResumeSummaryOut):
    parsed_data: dict[str, Any]
    ats_report: dict[str, Any]
    recruiter_audit: dict[str, Any]


class EnhanceBulletsRequest(BaseModel):
    resume_version_id: int | None = None
    bullets: list[str] = Field(default_factory=list, max_length=25)
    target_role: str | None = None


class JobMatchRequest(BaseModel):
    resume_version_id: int
    job_title: str = Field(..., min_length=2, max_length=160)
    company: str | None = Field(default=None, max_length=160)
    job_description: str = Field(..., min_length=30)


class SkillGapRequest(BaseModel):
    resume_version_id: int
    target_role: str | None = None
    job_description: str | None = None


class CareerPredictRequest(BaseModel):
    resume_version_id: int
    career_interests: list[str] = Field(default_factory=list)


class InterviewGenerateRequest(BaseModel):
    resume_version_id: int
    target_role: str = Field(default="Software Engineer", min_length=2, max_length=160)
    job_description: str | None = None
    difficulty: str = Field(default="mixed", pattern="^(junior|mid|senior|mixed)$")


class CareerTwinRequest(BaseModel):
    resume_version_id: int
    career_interests: list[str] = Field(default_factory=list)
    target_role: str | None = None


class VersionCompareRequest(BaseModel):
    base_version_id: int
    target_version_id: int
    job_description: str | None = None
