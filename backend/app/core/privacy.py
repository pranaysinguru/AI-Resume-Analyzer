"""File validation, PII protection, and secure in-memory upload handling."""

from __future__ import annotations

import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings

EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
PHONE_RE = re.compile(
    r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})|(?:\+?\d{1,3}[-.\s]?\d{5}[-.\s]?\d{5}))"
)
URL_RE = re.compile(r"https?://[^\s,;|]+", re.IGNORECASE)
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?", re.IGNORECASE)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+/?", re.IGNORECASE)


@dataclass(frozen=True)
class ValidatedUpload:
    """Metadata for a validated uploaded resume buffer."""

    filename: str
    extension: str
    content: bytes
    sha256: str


def validate_resume_upload(filename: str | None, content: bytes) -> ValidatedUpload:
    """Validate file name, extension, size, and binary signature before parsing."""
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must include a valid filename.",
        )

    safe_name = Path(filename).name
    ext = Path(safe_name).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF or DOCX resume.",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > settings.max_upload_bytes:
        limit_mb = settings.max_upload_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {limit_mb} MB maximum upload limit.",
        )

    if ext == ".pdf":
        if not content.lstrip().startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file: missing PDF header signature.",
            )
    elif ext == ".docx":
        if not content.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid DOCX file: file is not a valid ZIP-based Word document.",
            )
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                if "word/document.xml" not in zf.namelist():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid DOCX file: missing word/document.xml payload.",
                    )
        except zipfile.BadZipFile as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted DOCX archive could not be opened.",
            ) from exc

    digest = hashlib.sha256(content).hexdigest()
    return ValidatedUpload(
        filename=safe_name,
        extension=ext,
        content=content,
        sha256=digest,
    )


def mask_email(email: str) -> str:
    """Mask local part of an email address while preserving domain for verification."""
    local, _, domain = email.partition("@")
    if not domain:
        return "[email-redacted]"
    visible = local[:2] if len(local) > 2 else local[:1]
    return f"{visible}***@{domain}"


def mask_phone(phone: str) -> str:
    """Mask all but the last four digits of a phone number."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "[phone-redacted]"
    return f"***-***-{digits[-4:]}"


def redact_pii(text: str) -> str:
    """Replace raw emails and phone numbers in text with privacy-safe tokens."""
    sanitized = EMAIL_RE.sub(lambda m: mask_email(m.group(0)), text)
    sanitized = PHONE_RE.sub(lambda m: mask_phone(m.group(0)), sanitized)
    return sanitized
