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
from app.core.supabase import (
    get_supabase_admin,
)
from app.schemas.answer import (
    ProjectQuestionRequest,
    ProjectQuestionResponse,
)
from app.services.llm_answer_service import (
    LlmAnswerError,
)
from app.services.project_access_service import (
    get_accessible_project,
)
from app.services.project_answer_service import (
    answer_project_question,
)


router = APIRouter()


@router.post(
    "/projects/{project_id}/answer",
    response_model=ProjectQuestionResponse,
)
async def answer_project_document_question(
    project_id: UUID,
    request: ProjectQuestionRequest,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> ProjectQuestionResponse:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    try:
        return answer_project_question(
            supabase=supabase,
            project_id=str(project_id),
            question=request.question,
            search_limit=request.search_limit,
            minimum_similarity=(
                request.minimum_similarity
            ),
        )

    except LlmAnswerError as exc:
        raise HTTPException(
            status_code=(
                status
                .HTTP_502_BAD_GATEWAY
            ),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            "Project answer error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Proje sorusu yanıtlanırken "
                "hata oluştu."
            ),
        ) from exc