import json

from pydantic import ValidationError

from app.core.config import settings
from app.core.openai_client import (
    get_openai_client,
)
from app.prompts.question_resolution import (
    QUESTION_RESOLUTION_INSTRUCTIONS,
)
from app.schemas.question_resolution import (
    ResolvedConversationQuestion,
)
from app.services.conversation_context_service import (
    ContextMessage,
    render_conversation_context,
)


class QuestionResolutionError(
    RuntimeError
):
    pass


def resolve_conversation_question(
    *,
    question: str,
    context_messages: list[
        ContextMessage
    ],
) -> ResolvedConversationQuestion:
    normalized_question = question.strip()

    if (
        not settings
        .question_resolution_enabled
        or not context_messages
    ):
        return ResolvedConversationQuestion(
            is_follow_up=False,
            resolved_query=normalized_question,
            referenced_message_ids=[],
            resolution_confidence=1.0,
        )

    context = render_conversation_context(
        context_messages
    )

    input_text = f"""
KONUŞMA GEÇMİŞİ:
{context}

YENİ KULLANICI SORUSU:
{normalized_question}

Bu soruyu belge aramasında kullanılabilecek bağımsız
bir sorguya dönüştür.
"""

    client = get_openai_client()

    try:
        response = client.responses.create(
            model=(
                settings
                .question_resolution_model
            ),
            instructions=(
                QUESTION_RESOLUTION_INSTRUCTIONS
            ),
            input=input_text,
            text={
                "format": {
                    "type": "json_schema",
                    "name": (
                        "resolved_conversation_question"
                    ),
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "is_follow_up": {
                                "type": "boolean",
                            },
                            "resolved_query": {
                                "type": "string",
                            },
                            "referenced_message_ids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "resolution_confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                        "required": [
                            "is_follow_up",
                            "resolved_query",
                            "referenced_message_ids",
                            "resolution_confidence",
                        ],
                    },
                }
            },
            store=False,
        )

        parsed = json.loads(
            response.output_text
        )

        result = (
            ResolvedConversationQuestion
            .model_validate(parsed)
        )

    except (
        json.JSONDecodeError,
        ValidationError,
    ) as exc:
        raise QuestionResolutionError(
            "Takip sorusu geçerli biçimde "
            "çözümlenemedi."
        ) from exc

    except Exception as exc:
        raise QuestionResolutionError(
            "Takip sorusu çözümlenemedi."
        ) from exc

    valid_message_ids = {
        message.id
        for message in context_messages
    }

    filtered_ids = [
        message_id
        for message_id
        in result.referenced_message_ids
        if message_id in valid_message_ids
    ]

    resolved_query = (
        result.resolved_query.strip()
        or normalized_question
    )

    return ResolvedConversationQuestion(
        is_follow_up=(
            result.is_follow_up
        ),
        resolved_query=resolved_query,
        referenced_message_ids=(
            filtered_ids
        ),
        resolution_confidence=(
            result.resolution_confidence
        ),
    )