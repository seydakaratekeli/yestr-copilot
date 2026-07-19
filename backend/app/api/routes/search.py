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
from app.core.config import settings
from app.core.supabase import get_supabase_admin
from app.schemas.search import (
    AskProjectRequest,
    AskProjectResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
)
from app.services.embedding_service import (
    EmbeddingError,
)
from app.services.project_access_service import (
    get_accessible_project,
)
from app.services.llm_provider import (
    LLMConfigurationError,
    LLMGenerationError,
)
from app.services.rag_service import (
    ask_project_question,
)
from app.services.semantic_search_service import (
    SemanticSearchError,
    search_project_chunks,
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
        search_results = search_project_chunks(
            supabase=supabase,
            project_id=str(project_id),
            query=request.query,
            limit=request.limit,
            minimum_similarity=(
                request.minimum_similarity
            ),
        )
    except EmbeddingError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc
    except SemanticSearchError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc

    results = [
        SemanticSearchResult(
            id=result.id,
            document_id=result.document_id,
            project_id=result.project_id,
            page_number=result.page_number,
            chunk_index=result.chunk_index,
            content=result.content,
            document_type=result.document_type,
            original_filename=result.original_filename,
            extraction_method=result.extraction_method,
            similarity=result.similarity,
        )
        for result in search_results
    ]

    return SemanticSearchResponse(
        query=request.query,
        result_count=len(results),
        results=results,
    )


@router.post(
    "/projects/{project_id}/ask",
    response_model=AskProjectResponse,
)
async def ask_project(
    project_id: UUID,
    request: AskProjectRequest,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> AskProjectResponse:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    try:
        return ask_project_question(
            supabase=supabase,
            project_id=str(project_id),
            question=request.question,
            limit=(
                request.limit
                or settings.rag_search_limit
            ),
            minimum_similarity=(
                request.minimum_similarity
                if request.minimum_similarity is not None
                else settings.rag_minimum_similarity
            ),
        )
    except EmbeddingError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc
    except SemanticSearchError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(exc),
        ) from exc
    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
