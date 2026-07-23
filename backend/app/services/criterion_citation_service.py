from typing import Any

from app.services.rag_context_service import (
    RagSource,
)


def build_criterion_citations(
    *,
    citation_ids: list[str],
    sources: list[RagSource],
) -> list[dict[str, Any]]:
    source_map = {
        source.source_id: source
        for source in sources
    }

    citations: list[dict[str, Any]] = []

    for source_id in citation_ids:
        source = source_map.get(source_id)

        if source is None:
            continue

        citations.append(
            {
                "source_id": source.source_id,
                "chunk_id": source.chunk_id,
                "document_id": source.document_id,
                "original_filename": (
                    source.original_filename
                ),
                "document_type": (
                    source.document_type
                ),
                "page_number": source.page_number,
                "similarity": round(
                    source.similarity,
                    4,
                ),
                "extraction_method": (
                    source.extraction_method
                ),
                "excerpt": _build_excerpt(
                    source.content
                ),
            }
        )

    return citations


def _build_excerpt(
    content: str,
    limit: int = 500,
) -> str:
    normalized = " ".join(
        content.split()
    )

    if len(normalized) <= limit:
        return normalized

    return normalized[:limit].rstrip() + "..."