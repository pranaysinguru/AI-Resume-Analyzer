"""Pytest fixtures providing isolated temporary SQLite databases and synthetic PDF/DOCX resumes."""

from __future__ import annotations

import io
from pathlib import Path
import sys

import docx
import pymupdf
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "test_resumex.db"
    test_engine = create_engine(
        f"sqlite:///{db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    test_engine.dispose()


def build_sample_docx_bytes(strong: bool = True) -> bytes:
    """Create a realistic in-memory DOCX resume for automated testing."""
    document = docx.Document()
    document.add_paragraph("Alex Mercer")
    document.add_paragraph("alex.mercer@example.com | +1 555-345-6789 | github.com/alexmercer | linkedin.com/in/alexmercer")

    if strong:
        document.add_paragraph("SUMMARY")
        document.add_paragraph(
            "Full Stack and AI Engineer with 3 years of experience building Python FastAPI microservices, React TypeScript apps, and NLP pipelines."
        )
    document.add_paragraph("EXPERIENCE")
    document.add_paragraph("Software Engineer | Acme Cloud | Jan 2023 - Present")
    if strong:
        document.add_paragraph("• Engineered FastAPI and PostgreSQL microservices handling 12,000 requests/min and reduced p95 latency by 38%.")
        document.add_paragraph("• Automated CI/CD pipelines with Docker and Pytest, cutting release regressions by 45%.")
    else:
        document.add_paragraph("• Responsible for working on backend endpoints and helping with various database tasks.")

    document.add_paragraph("PROJECTS")
    document.add_paragraph("Semantic Talent Graph | 2024")
    if strong:
        document.add_paragraph("• Architected an NLP matching engine using Python, Sentence Transformers, and React TypeScript, achieving 91% retrieval precision.")
    else:
        document.add_paragraph("• Worked on a resume tool using Python.")

    document.add_paragraph("EDUCATION")
    document.add_paragraph("B.S. in Computer Science, State University (2019 - 2023)")

    document.add_paragraph("SKILLS")
    if strong:
        document.add_paragraph("Python, TypeScript, React, FastAPI, PostgreSQL, Docker, NLP, Sentence Transformers, Scikit-learn, Pytest, Git, System Design")
    else:
        document.add_paragraph("Python, Kubernetes, AWS, Terraform, React")

    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def build_sample_pdf_bytes() -> bytes:
    """Create a realistic in-memory PDF resume using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    text = (
        "Priya Sharma\n"
        "priya.sharma@domain.org | +1 415-888-9012 | github.com/priyasharma\n\n"
        "SUMMARY\n"
        "Machine Learning Engineer focused on NLP, PyTorch, and scalable API deployment.\n\n"
        "EXPERIENCE\n"
        "ML Engineer | DataPulse AI | Mar 2022 - Present\n"
        "- Built PyTorch and Hugging Face classification pipelines improving F1 score by 14% across 200,000 documents.\n"
        "- Deployed FastAPI inference services on Docker and AWS reducing inference cost by 28%.\n\n"
        "PROJECTS\n"
        "QueryLens RAG Engine | 2024\n"
        "- Implemented hybrid Vector Databases and Sentence Transformers search serving 1,500 users.\n\n"
        "EDUCATION\n"
        "M.S. Data Science, Tech Institute\n\n"
        "SKILLS\n"
        "Python, PyTorch, NLP, Sentence Transformers, Hugging Face, FastAPI, Docker, AWS, Pandas, NumPy, Scikit-learn"
    )
    page.insert_text((50, 50), text, fontsize=10)
    data = doc.tobytes()
    doc.close()
    return data
