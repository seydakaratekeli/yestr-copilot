from typing import Any, cast
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.auth import (
    AuthenticatedUser,
    get_current_user,
)
from app.core.supabase import get_supabase_admin
from app.schemas.search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
)
from app.services.embedding_service import (
    EmbeddingError,
    generate_query_embedding,
)
from app.services.project_access_service import (
    get_accessible_project,
)


router = APIRouter()


@router.post(
    "/projects/{project_id}/search",
    response_model=SemanticSearchResponse,
)
async def semantic_search_project(
    project_id: UUID,
    request: SemanticSearchRequest,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> SemanticSearchResponse:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    try:
        query_embedding = (
            generate_query_embedding(
                request.query
            )
        )
    except EmbeddingError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    try:
        response = supabase.rpc(
            "match_project_chunks",
            {
                "query_embedding": (
                    query_embedding
                ),
                "target_project_id": (
                    str(project_id)
                ),
                "match_count": request.limit,
                "minimum_similarity": (
                    request.minimum_similarity
                ),
            },
        ).execute()

    except Exception as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Semantik arama gerçekleştirilemedi."
            ),
        ) from exc

    results = [
        SemanticSearchResult(
            **result
        )
        for result in cast(list[dict[str, Any]], response.data or [])
    ]

    return SemanticSearchResponse(
        query=request.query,
        result_count=len(results),
        results=results,
    )