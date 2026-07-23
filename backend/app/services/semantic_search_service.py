from dataclasses import dataclass

from supabase import Client

from app.services.embedding_service import (
    generate_query_embedding,
)
from app.services.retry_service import (
    retry_transient,
)


class SemanticSearchError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    document_id: str
    project_id: str

    page_number: int
    chunk_index: int

    content: str

    document_type: str | None
    original_filename: str | None
    extraction_method: str | None

    similarity: float


def search_project_chunks(
    *,
    supabase: Client,
    project_id: str,
    query: str,
    limit: int,
    minimum_similarity: float,
) -> list[RetrievedChunk]:
    query_embedding = generate_query_embedding(
        query
    )

    try:
        response = retry_transient(
            lambda: supabase.rpc(
                "match_project_chunks",
                {
                    "query_embedding": query_embedding,
                    "target_project_id": project_id,
                    "match_count": limit,
                    "minimum_similarity": (
                        minimum_similarity
                    ),
                },
            ).execute(),
            operation_name=(
                "Proje parçalarında semantik arama"
            ),
        )
    except Exception as exc:
        raise SemanticSearchError(
            "Semantik arama gerçekleştirilemedi."
        ) from exc

    return [
        RetrievedChunk(
            id=row["id"],
            document_id=row["document_id"],
            project_id=row["project_id"],
            page_number=row["page_number"],
            chunk_index=row["chunk_index"],
            content=row["content"],
            document_type=row.get(
                "document_type"
            ),
            original_filename=row.get(
                "original_filename"
            ),
            extraction_method=row.get(
                "extraction_method"
            ),
            similarity=float(
                row["similarity"]
            ),
        )
        for row in (response.data or [])
    ]
