"""NLP embedding and spaCy pipeline singletons with offline-safe local cache."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_spacy_nlp() -> Any:
    """Load spaCy English pipeline once per process."""
    import spacy

    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("en_core_web_sm not found; falling back to blank English pipeline.")
        return spacy.blank("en")


@lru_cache(maxsize=1)
def get_sentence_model() -> Any | None:
    """Load local cached SentenceTransformer model if enabled."""
    if not settings.enable_dense_embeddings:
        return None
    try:
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        from sentence_transformers import SentenceTransformer

        try:
            return SentenceTransformer(
                settings.embedding_model_name,
                cache_folder=settings.models_cache_dir,
                local_files_only=True,
            )
        except Exception:
            return SentenceTransformer(
                settings.embedding_model_name,
                cache_folder=settings.models_cache_dir,
            )
    except Exception as exc:
        logger.warning("Dense embedding model unavailable (%s); using TF-IDF similarity.", exc)
        return None


def encode_texts(texts: list[str]) -> np.ndarray | None:
    """Encode a list of texts into L2-normalized dense vectors."""
    if not texts:
        return None
    model = get_sentence_model()
    if model is None:
        return None
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(embeddings, dtype=np.float32)


def compute_tfidf_similarity(text_a: str, text_b: str) -> tuple[float, list[dict[str, float | str]]]:
    """Compute TF-IDF cosine similarity and top shared contributing n-grams."""
    if not text_a.strip() or not text_b.strip():
        return 0.0, []
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=2000,
        sublinear_tf=True,
    )
    try:
        matrix = vectorizer.fit_transform([text_a, text_b])
    except ValueError:
        return 0.0, []

    sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    feature_names = vectorizer.get_feature_names_out()
    vec_a = matrix[0].toarray().ravel()
    vec_b = matrix[1].toarray().ravel()
    contributions = vec_a * vec_b
    top_indices = np.argsort(contributions)[::-1][:10]
    top_terms: list[dict[str, float | str]] = []
    for idx in top_indices:
        if contributions[idx] > 0:
            top_terms.append(
                {
                    "term": str(feature_names[idx]),
                    "contribution": round(float(contributions[idx]), 4),
                }
            )
    return max(0.0, min(1.0, sim)), top_terms


def compute_semantic_similarity(text_a: str, text_b: str) -> dict[str, object]:
    """Compute explainable hybrid semantic similarity (SentenceTransformer + TF-IDF)."""
    tfidf_sim, top_terms = compute_tfidf_similarity(text_a, text_b)
    vectors = encode_texts([text_a, text_b])

    if vectors is not None and len(vectors) == 2:
        dense_sim = float(np.dot(vectors[0], vectors[1]))
        dense_sim = max(0.0, min(1.0, dense_sim))
        hybrid = 0.72 * dense_sim + 0.28 * tfidf_sim
        mode = "hybrid_biencoder_tfidf"
    else:
        dense_sim = tfidf_sim
        hybrid = tfidf_sim
        mode = "tfidf_fallback"

    return {
        "hybrid_score": round(hybrid * 100, 1),
        "dense_similarity": round(dense_sim * 100, 1),
        "lexical_similarity": round(tfidf_sim * 100, 1),
        "mode": mode,
        "top_contributing_terms": top_terms,
    }


def batch_dense_similarity(query: str, candidates: list[str]) -> list[float]:
    """Compute similarity scores between a query and multiple candidate descriptions."""
    if not candidates or not query.strip():
        return [0.0 for _ in candidates]
    vectors = encode_texts([query, *candidates])
    if vectors is not None and len(vectors) == len(candidates) + 1:
        q_vec = vectors[0]
        c_vecs = vectors[1:]
        sims = c_vecs @ q_vec
        return [round(float(max(0.0, min(1.0, s))) * 100, 1) for s in sims]

    return [round(compute_tfidf_similarity(query, cand)[0] * 100, 1) for cand in candidates]
