"""Curated skill taxonomy, role archetypes, learning resources, and NLP skill extractor."""

from __future__ import annotations

import re
from dataclasses import dataclass

SKILL_CATALOG: dict[str, dict[str, list[str]]] = {
    "Programming Languages": {
        "Python": ["python", "py"],
        "TypeScript": ["typescript", "ts"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp"],
        "Go": ["golang", "go language"],
        "Rust": ["rust"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        "R": ["r programming", "rstudio"],
        "Scala": ["scala"],
        "Bash": ["bash", "shell scripting", "zsh"],
    },
    "Frontend & UI": {
        "React": ["react", "reactjs", "react.js"],
        "Next.js": ["next.js", "nextjs"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Angular": ["angular"],
        "Tailwind CSS": ["tailwind", "tailwind css", "tailwindcss"],
        "HTML5": ["html", "html5"],
        "CSS3": ["css", "css3", "scss", "sass"],
        "Redux": ["redux", "redux toolkit"],
        "Vite": ["vite"],
        "Accessibility": ["wcag", "a11y", "accessibility"],
    },
    "Backend & APIs": {
        "FastAPI": ["fastapi"],
        "Django": ["django", "drf", "django rest framework"],
        "Flask": ["flask"],
        "Node.js": ["node.js", "nodejs"],
        "Express.js": ["express", "express.js", "expressjs"],
        "Spring Boot": ["spring boot", "spring"],
        "GraphQL": ["graphql"],
        "REST APIs": ["rest", "restful", "rest api", "rest apis"],
        "Microservices": ["microservices", "microservice"],
        "gRPC": ["grpc"],
    },
    "AI, ML & NLP": {
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "neural networks", "neural network"],
        "NLP": ["nlp", "natural language processing"],
        "LLMs": ["llm", "llms", "large language models", "rag", "retrieval augmented generation"],
        "PyTorch": ["pytorch"],
        "TensorFlow": ["tensorflow", "keras"],
        "Scikit-learn": ["scikit-learn", "sklearn"],
        "spaCy": ["spacy"],
        "Hugging Face": ["hugging face", "huggingface", "transformers"],
        "Sentence Transformers": ["sentence transformers", "sentence-transformers", "embeddings"],
        "LangChain": ["langchain", "langgraph"],
        "Computer Vision": ["computer vision", "opencv", "yolo"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Feature Engineering": ["feature engineering"],
        "MLOps": ["mlops", "mlflow", "model deployment", "model monitoring"],
    },
    "Databases & Data": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "SQLite": ["sqlite"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "Elasticsearch": ["elasticsearch", "opensearch"],
        "Vector Databases": ["pinecone", "qdrant", "weaviate", "chromadb", "faiss", "pgvector"],
        "Apache Spark": ["spark", "pyspark", "apache spark"],
        "Apache Kafka": ["kafka", "apache kafka"],
        "Airflow": ["airflow", "apache airflow"],
        "dbt": ["dbt"],
        "BigQuery": ["bigquery"],
        "Snowflake": ["snowflake"],
        "ETL/ELT": ["etl", "elt", "data pipeline", "data pipelines"],
    },
    "Cloud, DevOps & Testing": {
        "Docker": ["docker", "containerization"],
        "Kubernetes": ["kubernetes", "k8s"],
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "ecs"],
        "GCP": ["gcp", "google cloud", "cloud run", "gke"],
        "Azure": ["azure"],
        "CI/CD": ["ci/cd", "github actions", "gitlab ci", "jenkins"],
        "Terraform": ["terraform", "iac", "infrastructure as code"],
        "Git": ["git", "github", "gitlab"],
        "Linux": ["linux", "ubuntu"],
        "Pytest": ["pytest", "unit testing", "integration testing"],
        "Jest": ["jest", "vitest", "playwright", "cypress"],
        "Monitoring": ["prometheus", "grafana", "datadog", "opentelemetry"],
    },
    "Security": {
        "OAuth2/JWT": ["oauth", "oauth2", "jwt", "oidc"],
        "OWASP": ["owasp", "appsec", "application security"],
        "Penetration Testing": ["penetration testing", "pentesting", "burp suite"],
        "IAM": ["iam", "rbac", "access control"],
    },
    "Soft Skills & Leadership": {
        "Technical Communication": ["communication", "documentation", "technical writing", "stakeholder"],
        "Cross-functional Collaboration": ["cross-functional", "collaborated", "collaboration", "teamwork"],
        "Leadership & Mentoring": ["led", "mentored", "leadership", "managed", "coached"],
        "Problem Solving": ["problem solving", "root cause", "troubleshooting", "debugging"],
        "Agile/Scrum": ["agile", "scrum", "kanban", "sprint"],
        "System Design": ["system design", "architecture", "scalability", "distributed systems"],
        "Product Thinking": ["product", "user research", "a/b testing", "experimentation"],
    },
}

SOFT_SKILL_CATEGORIES = {"Soft Skills & Leadership"}

SKILL_TO_CATEGORY: dict[str, str] = {}
ALIAS_LOOKUP: list[tuple[str, str, re.Pattern[str]]] = []

for category, skills in SKILL_CATALOG.items():
    for canonical, aliases in skills.items():
        SKILL_TO_CATEGORY[canonical] = category
        for alias in aliases:
            escaped = re.escape(alias)
            pattern = re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", re.IGNORECASE)
            ALIAS_LOOKUP.append((canonical, category, pattern))


@dataclass(frozen=True)
class RoleProfile:
    """Target role archetype used for career prediction and skill gap prioritization."""

    role: str
    summary: str
    core_skills: tuple[str, ...]
    preferred_skills: tuple[str, ...]
    soft_skills: tuple[str, ...]
    avg_project_signal: str


ROLE_PROFILES: tuple[RoleProfile, ...] = (
    RoleProfile(
        role="AI / Machine Learning Engineer",
        summary="Builds production ML/NLP models, embedding pipelines, and inference APIs.",
        core_skills=("Python", "Machine Learning", "PyTorch", "Scikit-learn", "NLP", "Pandas", "NumPy"),
        preferred_skills=("Sentence Transformers", "Hugging Face", "LLMs", "FastAPI", "Docker", "MLOps", "Vector Databases"),
        soft_skills=("System Design", "Problem Solving", "Technical Communication"),
        avg_project_signal="End-to-end ML training, evaluation metrics, and API deployment",
    ),
    RoleProfile(
        role="Full Stack Software Engineer",
        summary="Delivers end-to-end web products across modern frontend UIs, REST/GraphQL APIs, and relational databases.",
        core_skills=("TypeScript", "React", "Python", "FastAPI", "Node.js", "SQL", "PostgreSQL", "Git"),
        preferred_skills=("Tailwind CSS", "Next.js", "Docker", "REST APIs", "CI/CD", "Pytest", "Jest", "Redis"),
        soft_skills=("Cross-functional Collaboration", "System Design", "Agile/Scrum"),
        avg_project_signal="Deployed full-stack apps with auth, persistence, and automated tests",
    ),
    RoleProfile(
        role="Backend & API Engineer",
        summary="Architects high-throughput APIs, distributed data layers, and resilient cloud services.",
        core_skills=("Python", "FastAPI", "SQL", "PostgreSQL", "REST APIs", "Docker", "Git"),
        preferred_skills=("Microservices", "Redis", "Apache Kafka", "Kubernetes", "AWS", "CI/CD", "Pytest", "OAuth2/JWT"),
        soft_skills=("System Design", "Problem Solving", "Technical Communication"),
        avg_project_signal="Scalable API architecture, caching, query optimization, and reliability",
    ),
    RoleProfile(
        role="Frontend Engineer",
        summary="Crafts responsive, accessible, interactive interfaces and design systems.",
        core_skills=("TypeScript", "JavaScript", "React", "HTML5", "CSS3", "Tailwind CSS", "Git"),
        preferred_skills=("Next.js", "Vite", "Redux", "Jest", "Accessibility", "REST APIs", "GraphQL"),
        soft_skills=("Cross-functional Collaboration", "Product Thinking", "Technical Communication"),
        avg_project_signal="Component architecture, state management, performance, and UI polish",
    ),
    RoleProfile(
        role="Data Scientist",
        summary="Extracts actionable insights through statistical modeling, experimentation, and predictive analytics.",
        core_skills=("Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Machine Learning"),
        preferred_skills=("Feature Engineering", "Deep Learning", "NLP", "BigQuery", "Snowflake", "R"),
        soft_skills=("Technical Communication", "Product Thinking", "Problem Solving"),
        avg_project_signal="Exploratory analysis, hypothesis testing, model validation, and business impact",
    ),
    RoleProfile(
        role="Data Engineer",
        summary="Designs reliable ETL/ELT pipelines, streaming ingestion, and warehouse models.",
        core_skills=("Python", "SQL", "ETL/ELT", "PostgreSQL", "Apache Spark", "Airflow"),
        preferred_skills=("Apache Kafka", "dbt", "BigQuery", "Snowflake", "Docker", "AWS", "GCP"),
        soft_skills=("System Design", "Problem Solving", "Cross-functional Collaboration"),
        avg_project_signal="Automated ingestion pipelines, schema modeling, and data quality checks",
    ),
    RoleProfile(
        role="DevOps / Cloud Platform Engineer",
        summary="Automates CI/CD, container orchestration, infrastructure as code, and observability.",
        core_skills=("Docker", "Kubernetes", "CI/CD", "Linux", "Git", "AWS"),
        preferred_skills=("Terraform", "GCP", "Azure", "Monitoring", "Bash", "Python", "IAM"),
        soft_skills=("System Design", "Problem Solving", "Cross-functional Collaboration"),
        avg_project_signal="IaC provisioning, zero-downtime deployments, and telemetry dashboards",
    ),
    RoleProfile(
        role="Applied LLM / AI Product Engineer",
        summary="Integrates embeddings, RAG pipelines, and intelligent workflows into user-facing SaaS products.",
        core_skills=("Python", "LLMs", "NLP", "FastAPI", "React", "TypeScript", "Vector Databases"),
        preferred_skills=("Sentence Transformers", "Hugging Face", "LangChain", "Docker", "PostgreSQL", "REST APIs"),
        soft_skills=("Product Thinking", "System Design", "Technical Communication"),
        avg_project_signal="Production AI apps with grounded retrieval, evaluation, and clean UX",
    ),
)

LEARNING_RESOURCES: dict[str, dict[str, object]] = {
    "Python": {
        "resource": "Official Python Docs & Real Python Patterns",
        "url": "https://docs.python.org/3/tutorial/",
        "project": "Build an async CLI & REST data processor with strict type hints and pytest coverage.",
        "hours": 15,
    },
    "TypeScript": {
        "resource": "TypeScript Handbook (typescriptlang.org)",
        "url": "https://www.typescriptlang.org/docs/handbook/",
        "project": "Create a strongly typed API client and generic state store for a React dashboard.",
        "hours": 12,
    },
    "React": {
        "resource": "React Official Learn Guide (react.dev)",
        "url": "https://react.dev/learn",
        "project": "Build a multi-view analytics workspace with custom hooks, error boundaries, and charts.",
        "hours": 18,
    },
    "FastAPI": {
        "resource": "FastAPI Official Tutorial & Dependency Injection Guide",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "project": "Ship a modular FastAPI service with Pydantic v2 schemas, SQLAlchemy 2.0, and OpenAPI docs.",
        "hours": 12,
    },
    "Docker": {
        "resource": "Docker Getting Started & Multi-Stage Builds",
        "url": "https://docs.docker.com/get-started/",
        "project": "Containerize a FastAPI + React + PostgreSQL stack using multi-stage builds and Compose.",
        "hours": 10,
    },
    "Kubernetes": {
        "resource": "Kubernetes Basics Interactive Tutorials",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "project": "Deploy a 2-tier service locally on kind/minikube with health probes and HPA.",
        "hours": 18,
    },
    "PostgreSQL": {
        "resource": "PostgreSQL Indexing & Query Planning (Use The Index, Luke)",
        "url": "https://use-the-index-luke.com/",
        "project": "Optimize slow analytical queries with composite/GIN indexes and EXPLAIN ANALYZE benchmarks.",
        "hours": 12,
    },
    "PyTorch": {
        "resource": "PyTorch Official Tutorials",
        "url": "https://pytorch.org/tutorials/",
        "project": "Fine-tune a text classification encoder and log precision/recall and latency.",
        "hours": 20,
    },
    "Sentence Transformers": {
        "resource": "SBERT Documentation — Semantic Search & Bi-Encoders",
        "url": "https://www.sbert.net/",
        "project": "Build a hybrid BM25 + bi-encoder semantic matcher with cosine explainability.",
        "hours": 10,
    },
    "LLMs": {
        "resource": "Anthropic / Hugging Face Prompt & Evaluation Engineering Guides",
        "url": "https://huggingface.co/learn/nlp-course/",
        "project": "Implement a grounded RAG pipeline with citation checks and automated faithfulness evals.",
        "hours": 16,
    },
    "Vector Databases": {
        "resource": "Qdrant / pgvector Hybrid Search Guide",
        "url": "https://github.com/pgvector/pgvector",
        "project": "Index document chunks in pgvector/FAISS with metadata filtering and recall@k tests.",
        "hours": 10,
    },
    "CI/CD": {
        "resource": "GitHub Actions Documentation",
        "url": "https://docs.github.com/en/actions",
        "project": "Configure automated lint, pytest, typecheck, and Docker build workflows on every PR.",
        "hours": 8,
    },
    "AWS": {
        "resource": "AWS Well-Architected & Free-Tier Serverless Labs",
        "url": "https://docs.aws.amazon.com/",
        "project": "Deploy a containerized API on ECS/Lambda with S3 storage and least-privilege IAM.",
        "hours": 18,
    },
    "System Design": {
        "resource": "System Design Primer (GitHub)",
        "url": "https://github.com/donnemartin/system-design-primer",
        "project": "Document an architecture RFC covering caching, rate limiting, and failure modes.",
        "hours": 14,
    },
    "Pytest": {
        "resource": "Pytest Documentation — Fixtures & Parametrization",
        "url": "https://docs.pytest.org/en/stable/",
        "project": "Write unit and FastAPI TestClient integration suites with >85% branch coverage.",
        "hours": 8,
    },
}


def extract_skills(text: str) -> dict[str, object]:
    """Extract canonical technical and soft skills grouped by category."""
    found: dict[str, dict[str, object]] = {}
    for canonical, category, pattern in ALIAS_LOOKUP:
        matches = pattern.findall(text)
        if matches:
            existing = found.get(canonical)
            count = len(matches)
            if existing:
                existing["mentions"] = int(existing["mentions"]) + count
            else:
                found[canonical] = {
                    "skill": canonical,
                    "category": category,
                    "is_soft_skill": category in SOFT_SKILL_CATEGORIES,
                    "mentions": count,
                }

    technical = sorted(
        [v for v in found.values() if not v["is_soft_skill"]],
        key=lambda item: (-int(item["mentions"]), str(item["skill"])),
    )
    soft = sorted(
        [v for v in found.values() if v["is_soft_skill"]],
        key=lambda item: (-int(item["mentions"]), str(item["skill"])),
    )
    all_names = [str(item["skill"]) for item in technical + soft]

    by_category: dict[str, list[str]] = {}
    for item in technical + soft:
        cat = str(item["category"])
        by_category.setdefault(cat, []).append(str(item["skill"]))

    return {
        "technical_skills": technical,
        "soft_skills": soft,
        "all_skills": all_names,
        "by_category": by_category,
    }


def get_learning_recommendation(skill: str) -> dict[str, object]:
    """Return a concrete learning resource and hands-on project for a missing skill."""
    if skill in LEARNING_RESOURCES:
        return dict(LEARNING_RESOURCES[skill])
    category = SKILL_TO_CATEGORY.get(skill, "Core Engineering")
    return {
        "resource": f"Official {skill} Documentation & Hands-On Applied Practice ({category})",
        "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+official+documentation",
        "project": f"Build and document a portfolio mini-project integrating {skill} with automated tests and measurable benchmarks.",
        "hours": 12,
    }
