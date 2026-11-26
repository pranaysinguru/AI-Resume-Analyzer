"""Application configuration for ResumeX AI."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings with SQLite default and PostgreSQL-ready URL override."""

    app_name: str = "ResumeX AI"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{(BASE_DIR / 'resumex.db').as_posix()}"
    models_cache_dir: str = str(BASE_DIR / "models_cache")
    max_upload_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: tuple[str, ...] = (".pdf", ".docx")
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ]
    enable_dense_embeddings: bool = True
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_prefix="RESUMEX_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
