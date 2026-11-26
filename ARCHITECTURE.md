# ResumeX AI — System Architecture

## 1. Overview
**ResumeX AI** is a full-stack, explainable AI career intelligence platform built with a decoupled FastAPI backend and a React + TypeScript + Tailwind CSS frontend.

## 2. Repository Layout
```text
AI RESUME ANALYZER/
├── ARCHITECTURE.md
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint, CORS, lifecycle, routers
│   │   ├── core/
│   │   │   ├── config.py            # Settings (DB URL, upload limits, PII privacy mode)
│   │   │   ├── database.py          # SQLAlchemy engine & session (SQLite / PostgreSQL ready)
│   │   │   └── privacy.py           # PII redaction & secure temp-file handling
│   │   ├── models/
│   │   │   └── entities.py          # ORM tables: Resumes, Versions, Analyses, JobMatches, CareerTwins, Interviews
│   │   ├── schemas/
│   │   │   └── contracts.py         # Pydantic v2 request/response contracts
│   │   ├── nlp/
│   │   │   ├── parser.py            # PyMuPDF + python-docx extraction & section segmentation
│   │   │   ├── embeddings.py        # SentenceTransformer / TF-IDF+SVD hybrid semantic engine
│   │   │   ├── skill_taxonomy.py    # Curated + spaCy-assisted skill & role taxonomy
│   │   │   └── explainability.py    # Feature-level score attribution & deterministic breakdowns
│   │   ├── services/
│   │   │   ├── ats_simulator.py     # Explainable ATS scoring (format, keywords, impact, structure)
│   │   │   ├── job_matcher.py       # Semantic + lexical JD matching & gap analysis
│   │   │   ├── skill_roadmap.py     # Prioritized skill gaps, projects & learning resources
│   │   │   ├── enhancer.py          # Grounded bullet rewriting (no fabrication of metrics/facts)
│   │   │   ├── career_predictor.py  # Role prediction with evidence-backed reasoning
│   │   │   ├── interview_sim.py     # Tailored technical, HR, behavioral & project questions
│   │   │   ├── recruiter_mode.py    # Skeptical recruiter audit (red flags, weak proof, clarity)
│   │   │   ├── version_diff.py      # Multi-version comparison & delta tracking
│   │   │   └── career_twin.py       # Evidence-backed Career Twin graph & planner
│   │   └── api/
│   │       └── routes/
│   │           ├── resumes.py       # Upload, parse, list, delete, versions, diff
│   │           ├── analysis.py      # ATS, Recruiter Mode, Bullet Enhancer
│   │           ├── matching.py      # Job Matching, Skill Gaps, Career Prediction
│   │           ├── interview.py     # Personalized AI Interview Simulator
│   │           ├── twin.py          # Career Twin synthesis & interactive exploration
│   │           └── dashboard.py     # Live aggregated analytics from persisted records
│   └── tests/
│       └── ...                      # Pytest suite (unit + integration + edge cases)
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    └── src/
        ├── api/                     # Typed API client
        ├── components/              # Reusable UI, charts (Recharts), upload dropzone, theme toggle
        ├── pages/                   # Landing, Dashboard, Analyzer, Job Match, Career Twin, Interview, Versions
        └── types/                   # Shared TypeScript interfaces matching backend contracts
```

## 3. Data & Privacy Principles
- **Database Portability:** SQLAlchemy 2.0 ORM with `DATABASE_URL` defaulting to `sqlite:///./resumex.db` and directly switchable to `postgresql+psycopg://...`.
- **PII Protection:** Uploaded raw files are validated (extension, magic bytes/structure, size limit), processed in memory/ephemeral storage, and personal contact fields (email, phone, street address) are masked/redacted in analytics logs and optional privacy-safe previews.
- **No Fabrication Guarantee:** The Resume Enhancer transforms phrasing, action verbs, and structure while inserting explicit `[metric placeholder]` prompts where numbers are missing rather than inventing fake achievements.
- **Explainable Scoring:** Every ATS, Job Match, and Career Prediction score returns exact sub-scores, weights, matched tokens, and evidence spans from the resume.
