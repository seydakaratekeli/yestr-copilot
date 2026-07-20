from app.schemas.conversation import (
    ConversationMessage,
    ConversationSummary,
)


def map_conversation_summary(
    row: dict,
) -> ConversationSummary:
    return ConversationSummary(
        id=row["id"],
        project_id=row["project_id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def map_conversation_message(
    row: dict,
) -> ConversationMessage:
    return ConversationMessage(
        id=row["id"],
        conversation_id=row["conversation_id"],
        project_id=row["project_id"],
        role=row["role"],
        content=row["content"],
        answer_status=row.get("answer_status"),
        confidence=(
            float(row["confidence"])
            if row.get("confidence") is not None
            else None
        ),
        citations=row.get("citations") or [],
        missing_information=(
            row.get("missing_information") or []
        ),
        warnings=row.get("warnings") or [],
        retrieved_source_count=(
            row.get("retrieved_source_count") or 0
        ),
        error_message=row.get("error_message"),
        created_at=row["created_at"],
    )