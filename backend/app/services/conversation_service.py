from datetime import datetime, timezone

from fastapi import HTTPException, status
from supabase import Client


def create_conversation(
    *,
    supabase: Client,
    project_id: str,
    user_id: str,
    title: str | None = None,
) -> dict:
    final_title = (
        title.strip()
        if title and title.strip()
        else "Yeni konuşma"
    )

    response = (
        supabase
        .table("project_conversations")
        .insert(
            {
                "project_id": project_id,
                "created_by": user_id,
                "title": final_title,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Konuşma oluşturulamadı."
        )

    return response.data[0]


def get_accessible_conversation(
    *,
    supabase: Client,
    conversation_id: str,
    project_id: str,
    user_id: str,
) -> dict:
    response = (
        supabase
        .table("project_conversations")
        .select(
            "id, project_id, created_by, title, "
            "created_at, updated_at"
        )
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konuşma bulunamadı.",
        )

    conversation = response.data[0]

    if conversation["created_by"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu konuşmaya erişim yetkiniz yok.",
        )

    return conversation


def insert_user_message(
    *,
    supabase: Client,
    conversation_id: str,
    project_id: str,
    content: str,
) -> dict:
    response = (
        supabase
        .table("conversation_messages")
        .insert(
            {
                "conversation_id": conversation_id,
                "project_id": project_id,
                "role": "user",
                "content": content,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Kullanıcı mesajı kaydedilemedi."
        )

    _touch_conversation(
        supabase=supabase,
        conversation_id=conversation_id,
    )

    return response.data[0]


def insert_assistant_message(
    *,
    supabase: Client,
    conversation_id: str,
    project_id: str,
    content: str,
    answer_status: str,
    confidence: float,
    citations: list[dict],
    missing_information: list[str],
    warnings: list[str],
    retrieved_source_count: int,
    error_message: str | None = None,
) -> dict:
    response = (
        supabase
        .table("conversation_messages")
        .insert(
            {
                "conversation_id": conversation_id,
                "project_id": project_id,
                "role": "assistant",
                "content": content,
                "answer_status": answer_status,
                "confidence": confidence,
                "citations": citations,
                "missing_information": (
                    missing_information
                ),
                "warnings": warnings,
                "retrieved_source_count": (
                    retrieved_source_count
                ),
                "error_message": error_message,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Asistan mesajı kaydedilemedi."
        )

    _touch_conversation(
        supabase=supabase,
        conversation_id=conversation_id,
    )

    return response.data[0]


def update_conversation_title_from_question(
    *,
    supabase: Client,
    conversation_id: str,
    question: str,
) -> None:
    response = (
        supabase
        .table("project_conversations")
        .select("title")
        .eq("id", conversation_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return

    if response.data[0]["title"] != "Yeni konuşma":
        return

    normalized = " ".join(question.split())

    title = (
        normalized[:77] + "..."
        if len(normalized) > 80
        else normalized
    )

    (
        supabase
        .table("project_conversations")
        .update(
            {
                "title": title,
                "updated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        )
        .eq("id", conversation_id)
        .execute()
    )


def _touch_conversation(
    *,
    supabase: Client,
    conversation_id: str,
) -> None:
    (
        supabase
        .table("project_conversations")
        .update(
            {
                "updated_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        )
        .eq("id", conversation_id)
        .execute()
    )