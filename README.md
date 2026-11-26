# ResumeX AI — Next-Generation Career Intelligence Platform

**ResumeX AI** is a full-stack, explainable AI Resume Analyzer and Career Twin platform built with **FastAPI**, **Sentence Transformers**, **spaCy**, **Scikit-learn**, **SQLAlchemy**, and **React + TypeScript + Tailwind CSS + Recharts**.

## Key Capabilities
1. **Advanced Resume Intelligence** — In-memory PDF (`PyMuPDF`) & DOCX (`python-docx`) parsing, section segmentation, strength/weakness diagnostics, and automatic PII masking.
2. **Intelligent ATS Simulator** — Deterministic, explainable 5-dimension scoring with weighted point attribution and prioritized uplift fixes.
3. **AI Job Matching** — Hybrid `all-MiniLM-L6-v2` bi-encoder + TF-IDF semantic similarity mapping job requirements to exact resume bullets.
4. **Skill Gap Intelligence** — Prioritized technical & soft skill gaps with phased 6-week learning roadmaps and hands-on portfolio projects.
5. **AI Resume Enhancement (Zero-Fabrication)** — Upgrades weak bullet phrasing and action verbs while using explicit `[insert real metric]` prompts instead of inventing experience.
6. **Career Prediction & Recommendations** — Evidence-backed role recommendations with transparent reasoning.
7. **AI Interview Simulator** — Personalized technical, project deep-dive, behavioral, and HR questions anchored to your real resume and target JD.
8. **Resume Version Intelligence** — Track ATS, skill evidence, bullet quality, and job-match deltas across resume iterations.
9. **Recruiter Perspective Mode** — 7-second scan and critical hiring-manager audit exposing skill inflation and unverified claims.
10. **Career Intelligence Dashboard** — Live analytics powered exclusively by persisted SQLite/PostgreSQL records.
11. **Intelligent Career Twin** — Evidence-backed digital twin separating verified skills from declared-only skills with a 30-60-90 day roadmap.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for system architecture details.

---

## Running Locally on Windows

### 1. Start the FastAPI Backend
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
API docs will be available at `http://127.0.0.1:8000/docs`.

### 2. Start the React Frontend
```powershell
cd frontend
npm.cmd run dev
```
Open `http://localhost:5173` in your browser. (Vite automatically proxies `/api` requests to `http://127.0.0.1:8000`.)

### 3. Run Automated Tests
**Backend (Pytest):**
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```

**Frontend (TypeScript + Build + Vitest):**
```powershell
cd frontend
npm.cmd run build
npm.cmd test
```

### PostgreSQL Readiness
Update `RESUMEX_DATABASE_URL` in `backend/.env` (see `backend/.env.example`) to point to PostgreSQL without modifying any application code.
