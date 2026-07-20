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
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationDetail,
    ConversationQuestionRequest,
    ConversationQuestionResponse,
    ConversationSummary,
)
from app.services.conversation_mapper import (
    map_conversation_message,
    map_conversation_summary,
)
from app.services.conversation_service import (
    create_conversation,
    get_accessible_conversation,
    insert_assistant_message,
    insert_user_message,
    update_conversation_title_from_question,
)
from app.services.project_access_service import (
    get_accessible_project,
)
from app.services.project_answer_service import (
    answer_project_question,
)


router = APIRouter()


@router.get(
    "/projects/{project_id}/conversations",
    response_model=list[ConversationSummary],
)
async def list_project_conversations(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> list[ConversationSummary]:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    response = (
        supabase
        .table("project_conversations")
        .select(
            "id, project_id, title, "
            "created_at, updated_at"
        )
        .eq("project_id", str(project_id))
        .eq("created_by", current_user.id)
        .order("updated_at", desc=True)
        .execute()
    )

    return [
        map_conversation_summary(row)
        for row in (response.data or [])
    ]


@router.post(
    "/projects/{project_id}/conversations",
    response_model=ConversationSummary,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_conversation(
    project_id: UUID,
    request: ConversationCreateRequest,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> ConversationSummary:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    conversation = create_conversation(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
        title=request.title,
    )

    return map_conversation_summary(
        conversation
    )


@router.get(
    "/projects/{project_id}/conversations/"
    "{conversation_id}",
    response_model=ConversationDetail,
)
async def get_conversation_detail(
    project_id: UUID,
    conversation_id: UUID,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> ConversationDetail:
    supabase = get_supabase_admin()

    conversation = get_accessible_conversation(
        supabase=supabase,
        conversation_id=str(conversation_id),
        project_id=str(project_id),
        user_id=current_user.id,
    )

    messages_response = (
        supabase
        .table("conversation_messages")
        .select("*")
        .eq(
            "conversation_id",
            str(conversation_id),
        )
        .order("created_at")
        .execute()
    )

    return ConversationDetail(
        conversation=map_conversation_summary(
            conversation
        ),
        messages=[
            map_conversation_message(row)
            for row in (
                messages_response.data or []
            )
        ],
    )


@router.post(
    "/projects/{project_id}/conversations/"
    "{conversation_id}/messages",
    response_model=ConversationQuestionResponse,
)
async def ask_conversation_question(
    project_id: UUID,
    conversation_id: UUID,
    request: ConversationQuestionRequest,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> ConversationQuestionResponse:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    get_accessible_conversation(
        supabase=supabase,
        conversation_id=str(conversation_id),
        project_id=str(project_id),
        user_id=current_user.id,
    )

    user_message_row = insert_user_message(
        supabase=supabase,
        conversation_id=str(conversation_id),
        project_id=str(project_id),
        content=request.question,
    )

    update_conversation_title_from_question(
        supabase=supabase,
        conversation_id=str(conversation_id),
        question=request.question,
    )

    try:
        answer = answer_project_question(
            supabase=supabase,
            project_id=str(project_id),
            question=request.question,
            search_limit=request.search_limit,
            minimum_similarity=(
                request.minimum_similarity
            ),
        )

        assistant_message_row = (
            insert_assistant_message(
                supabase=supabase,
                conversation_id=(
                    str(conversation_id)
                ),
                project_id=str(project_id),
                content=answer.answer,
                answer_status=answer.status,
                confidence=answer.confidence,
                citations=[
                    citation.model_dump(
                        mode="json"
                    )
                    for citation in (
                        answer.citations
                    )
                ],
                missing_information=(
                    answer.missing_information
                ),
                warnings=answer.warnings,
                retrieved_source_count=(
                    answer
                    .retrieved_source_count
                ),
            )
        )

    except Exception as exc:
        assistant_message_row = (
            insert_assistant_message(
                supabase=supabase,
                conversation_id=(
                    str(conversation_id)
                ),
                project_id=str(project_id),
                content=(
                    "Soru işlenirken bir hata oluştu. "
                    "Lütfen tekrar deneyin."
                ),
                answer_status="failed",
                confidence=0,
                citations=[],
                missing_information=[],
                warnings=[],
                retrieved_source_count=0,
                error_message=str(exc)[:1000],
            )
        )

        print(
            "Conversation answer error:",
            repr(exc),
        )

    return ConversationQuestionResponse(
        conversation_id=str(conversation_id),
        user_message=map_conversation_message(
            user_message_row
        ),
        assistant_message=(
            map_conversation_message(
                assistant_message_row
            )
        ),
    )