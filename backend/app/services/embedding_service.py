from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    if not settings.embedding_enabled:
        raise EmbeddingError(
            "Embedding sistemi devre dışı."
        )

    try:
        return SentenceTransformer(
            settings.embedding_model
        )
    except Exception as exc:
        raise EmbeddingError(
            "Embedding modeli yüklenemedi."
        ) from exc


def generate_document_embeddings(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []

    model = get_embedding_model()

    prepared_texts = [
        f"passage: {text.strip()}"
        for text in texts
    ]

    try:
        vectors = model.encode(
            prepared_texts,
            batch_size=settings.embedding_batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
    except Exception as exc:
        raise EmbeddingError(
            "Belge embedding'leri üretilemedi."
        ) from exc

    return _convert_vectors(vectors)


def generate_query_embedding(
    query: str,
) -> list[float]:
    normalized_query = query.strip()

    if not normalized_query:
        raise EmbeddingError(
            "Arama sorgusu boş olamaz."
        )

    model = get_embedding_model()

    try:
        vector = model.encode(
            [f"query: {normalized_query}"],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )[0]
    except Exception as exc:
        raise EmbeddingError(
            "Sorgu embedding'i üretilemedi."
        ) from exc

    result = vector.astype(
        np.float32
    ).tolist()

    _validate_dimension(result)

    return result


def _convert_vectors(
    vectors: np.ndarray,
) -> list[list[float]]:
    results: list[list[float]] = []

    for vector in vectors:
        result = vector.astype(
            np.float32
        ).tolist()

        _validate_dimension(result)

        results.append(result)

    return results


def _validate_dimension(
    vector: list[float],
) -> None:
    if len(vector) != settings.embedding_dimension:
        raise EmbeddingError(
            "Embedding boyutu beklenen değerle "
            "eşleşmiyor. "
            f"Beklenen: {settings.embedding_dimension}, "
            f"alınan: {len(vector)}"
        )