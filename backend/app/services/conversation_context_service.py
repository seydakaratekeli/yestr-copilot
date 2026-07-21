from dataclasses import dataclass

from supabase import Client

from app.core.config import settings


@dataclass(frozen=True)
class ContextMessage:
    id: str
    role: str
    content: str
    created_at: str


def get_recent_conversation_context(
    *,
    supabase: Client,
    conversation_id: str,
    exclude_message_id: str | None = None,
) -> list[ContextMessage]:
    query = (
        supabase
        .table("conversation_messages")
        .select(
            "id, role, content, created_at"
        )
        .eq(
            "conversation_id",
            conversation_id,
        )
        .order(
            "created_at",
            desc=True,
        )
        .limit(
            settings
            .conversation_context_message_limit
        )
    )

    if exclude_message_id:
        query = query.neq(
            "id",
            exclude_message_id,
        )

    response = query.execute()

    rows = list(
        reversed(response.data or [])
    )

    messages: list[ContextMessage] = []
    total_characters = 0

    for row in rows:
        content = str(
            row["content"]
        ).strip()

        if not content:
            continue

        remaining = (
            settings
            .conversation_context_character_limit
            - total_characters
        )

        if remaining <= 0:
            break

        if len(content) > remaining:
            content = content[:remaining]

        messages.append(
            ContextMessage(
                id=row["id"],
                role=row["role"],
                content=content,
                created_at=row["created_at"],
            )
        )

        total_characters += len(content)

    return messages


def render_conversation_context(
    messages: list[ContextMessage],
) -> str:
    rendered: list[str] = []

    for message in messages:
        role_label = (
            "KULLANICI"
            if message.role == "user"
            else "ASİSTAN"
        )

        rendered.append(
            "\n".join(
                [
                    f"MESSAGE_ID: {message.id}",
                    f"ROLE: {role_label}",
                    f"CONTENT: {message.content}",
                ]
            )
        )

    return "\n\n---\n\n".join(
        rendered
    )