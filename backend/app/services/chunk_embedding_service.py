from datetime import datetime, timezone
from typing import Any, cast

from app.core.config import settings
from app.core.supabase import get_supabase_admin
from app.services.embedding_service import (
    EmbeddingError,
    generate_document_embeddings,
)


def embed_document_chunks(
    *,
    document_id: str,
) -> None:
    supabase = get_supabase_admin()

    try:
        response = (
            supabase
            .table("document_chunks")
            .select(
                "id, content, embedding_status"
            )
            .eq("document_id", document_id)
            .eq("is_searchable", True)
            .in_(
                "embedding_status",
                ["pending", "failed"],
            )
            .order("page_number")
            .order("chunk_index")
            .execute()
        )

        chunks = cast(list[dict[str, Any]], response.data or [])

        if not chunks:
            return

        chunk_ids = [
            chunk["id"]
            for chunk in chunks
        ]

        (
            supabase
            .table("document_chunks")
            .update(
                {
                    "embedding_status": (
                        "processing"
                    ),
                    "embedding_error": None,
                }
            )
            .in_("id", chunk_ids)
            .execute()
        )

        batch_size = settings.embedding_batch_size

        for start in range(
            0,
            len(chunks),
            batch_size,
        ):
            batch = chunks[
                start:start + batch_size
            ]

            texts = [
                str(chunk["content"])
                for chunk in batch
            ]

            vectors = (
                generate_document_embeddings(
                    texts
                )
            )

            for chunk, vector in zip(
                batch,
                vectors,
                strict=True,
            ):
                (
                    supabase
                    .table("document_chunks")
                    .update(
                        {
                            "embedding": vector,
                            "embedding_model": (
                                settings.embedding_model
                            ),
                            "embedding_status": (
                                "completed"
                            ),
                            "embedding_created_at": (
                                datetime.now(
                                    timezone.utc
                                ).isoformat()
                            ),
                            "embedding_error": None,
                        }
                    )
                    .eq("id", chunk["id"])
                    .execute()
                )

    except EmbeddingError as exc:
        _mark_embedding_failure(
            document_id=document_id,
            message=str(exc),
        )

    except Exception as exc:
        _mark_embedding_failure(
            document_id=document_id,
            message=(
                "Embedding işlemi sırasında "
                f"hata oluştu: {exc}"
            ),
        )


def _mark_embedding_failure(
    *,
    document_id: str,
    message: str,
) -> None:
    supabase = get_supabase_admin()

    (
        supabase
        .table("document_chunks")
        .update(
            {
                "embedding_status": "failed",
                "embedding_error": (
                    message[:1000]
                ),
            }
        )
        .eq("document_id", document_id)
        .eq("embedding_status", "processing")
        .execute()
    )

    print(
        f"Embedding generation failed "
        f"for document {document_id}: "
        f"{message}"
    )