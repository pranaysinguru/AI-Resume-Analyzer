"""End-to-end API integration tests covering all 11 ResumeX AI capabilities."""

from __future__ import annotations

from tests.conftest import build_sample_docx_bytes, build_sample_pdf_bytes


def test_empty_dashboard_has_zero_stats(client):
    resp = client.get("/api/v1/dashboard/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body["has_data"] is False
    assert body["summary_metrics"]["total_versions"] == 0
    assert body["summary_metrics"]["latest_ats_score"] == 0.0


def test_full_platform_workflow(client):
    # 1. Upload v1 (weak) and v2 (strong) under the same profile
    weak_bytes = build_sample_docx_bytes(strong=False)
    v1_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume_v1.docx", weak_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={"version_label": "v1 Draft", "target_role": "Full Stack Software Engineer"},
    )
    assert v1_resp.status_code == 201
    v1 = v1_resp.json()
    assert v1["ats_score"] > 0
    profile_id = v1["profile_id"]

    strong_bytes = build_sample_docx_bytes(strong=True)
    v2_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume_v2.docx", strong_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={
            "profile_id": str(profile_id),
            "version_label": "v2 Quantified",
            "target_role": "Full Stack Software Engineer",
        },
    )
    assert v2_resp.status_code == 201
    v2 = v2_resp.json()
    assert v2["version_number"] == 2
    assert v2["ats_score"] > v1["ats_score"]

    # 2. Check ATS & Recruiter Perspective Mode
    ats_resp = client.get(f"/api/v1/analysis/{v2['id']}/ats")
    assert ats_resp.status_code == 200
    assert len(ats_resp.json()["dimensions"]) == 5

    recruiter_resp = client.get(f"/api/v1/analysis/{v1['id']}/recruiter")
    assert recruiter_resp.status_code == 200
    assert len(recruiter_resp.json()["red_flags"]) >= 1

    # 3. AI Job Matching
    jd = (
        "We are hiring a Full Stack AI Engineer with 2+ years experience in Python, FastAPI, React, "
        "TypeScript, PostgreSQL, Docker, Kubernetes, and Sentence Transformers to build scalable NLP SaaS APIs."
    )
    match_resp = client.post(
        "/api/v1/matching/job-match",
        json={
            "resume_version_id": v2["id"],
            "job_title": "Full Stack AI Engineer",
            "company": "NovaAI",
            "job_description": jd,
        },
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()
    assert "Python" in match_data["matched_skills"]
    assert "Kubernetes" in match_data["missing_skills"]
    assert match_data["overall_match_score"] > 40

    # 4. Skill Gap Intelligence
    gap_resp = client.post(
        "/api/v1/matching/skill-gaps",
        json={"resume_version_id": v2["id"], "target_role": "Full Stack Software Engineer", "job_description": jd},
    )
    assert gap_resp.status_code == 200
    gaps = gap_resp.json()
    assert any(g["skill"] == "Kubernetes" for g in gaps["technical_gaps"])
    assert len(gaps["roadmap"]) == 3

    # 5. Bullet Enhancer
    enh_resp = client.post(
        "/api/v1/analysis/enhance-bullets",
        json={"resume_version_id": v1["id"], "target_role": "Backend Engineer"},
    )
    assert enh_resp.status_code == 200
    assert enh_resp.json()["count"] >= 1

    # 6. Career Prediction
    pred_resp = client.post(
        "/api/v1/matching/career-predict",
        json={"resume_version_id": v2["id"], "career_interests": ["AI", "Backend"]},
    )
    assert pred_resp.status_code == 200
    assert len(pred_resp.json()["recommendations"]) >= 3

    # 7. AI Interview Simulator
    int_resp = client.post(
        "/api/v1/interview/generate",
        json={"resume_version_id": v2["id"], "target_role": "Full Stack AI Engineer", "job_description": jd},
    )
    assert int_resp.status_code == 200
    questions = int_resp.json()["questions"]
    assert len(questions) >= 6
    assert {"Technical", "Project Deep Dive", "Behavioral", "HR"}.issubset({q["category"] for q in questions})

    # 8. Version Intelligence Diff
    diff_resp = client.post(
        "/api/v1/resumes/compare",
        json={"base_version_id": v1["id"], "target_version_id": v2["id"], "job_description": jd},
    )
    assert diff_resp.status_code == 200
    diff_data = diff_resp.json()
    assert diff_data["ats_score_delta"] > 0
    assert diff_data["job_compatibility_delta"]["delta"] > 0

    # 9. Career Twin
    twin_resp = client.post(
        "/api/v1/twin/synthesize",
        json={"resume_version_id": v2["id"], "career_interests": ["NLP", "FastAPI"]},
    )
    assert twin_resp.status_code == 200
    twin = twin_resp.json()
    assert twin["twin_health_score"] > 0
    assert len(twin["action_plan_30_60_90"]) == 3

    # 10. Dashboard reflects live persisted metrics
    dash_resp = client.get(f"/api/v1/dashboard/overview?resume_id={v2['id']}")
    assert dash_resp.status_code == 200
    dash = dash_resp.json()
    assert dash["has_data"] is True
    assert dash["summary_metrics"]["total_versions"] == 2
    assert dash["summary_metrics"]["total_job_matches"] == 1
    assert dash["summary_metrics"]["interview_sessions_count"] == 1

    # 11. PDF Upload & Delete works cleanly
    pdf_resp = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("priya.pdf", build_sample_pdf_bytes(), "application/pdf")},
    )
    assert pdf_resp.status_code == 201
    pdf_id = pdf_resp.json()["id"]
    del_resp = client.delete(f"/api/v1/resumes/{pdf_id}")
    assert del_resp.status_code == 200
    assert client.get(f"/api/v1/resumes/{pdf_id}").status_code == 404
