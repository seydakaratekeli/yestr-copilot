import json

from pydantic import ValidationError

from app.core.config import settings
from app.core.openai_client import (
    get_openai_client,
)
from app.prompts.grounded_answer import (
    GROUNDED_ANSWER_INSTRUCTIONS,
)
from app.schemas.llm_answer import (
    LlmGroundedAnswer,
)
from app.services.rag_context_service import (
    RagSource,
    render_rag_context,
)


class LlmAnswerError(RuntimeError):
    pass


def generate_grounded_answer(
    *,
    question: str,
    resolved_query: str,
    sources: list[RagSource],
    conversation_context: str | None = None,
) -> LlmGroundedAnswer:
    if not settings.llm_enabled:
        raise LlmAnswerError(
            "LLM cevap sistemi devre dışı."
        )

    if not sources:
        return LlmGroundedAnswer(
            status="insufficient_evidence",
            answer=(
                "Yüklenen proje belgelerinde bu "
                "soruyu yanıtlayacak yeterli bilgi "
                "bulunamadı."
            ),
            confidence=0.0,
            citation_ids=[],
            missing_information=[
                (
                    "Soruyla ilişkili proje belgesi "
                    "veya teknik veri bulunamadı."
                )
            ],
            warnings=[],
        )

    context = render_rag_context(sources)

    context_section = (
        conversation_context
        if conversation_context
        else "Konuşma bağlamı bulunmuyor."
    )

    user_input = f"""
KONUŞMA BAĞLAMI:
{context_section}

KULLANICININ GÜNCEL SORUSU:
{question}

BELGE ARAMASINDA KULLANILAN BAĞIMSIZ SORGU:
{resolved_query}

KAYNAKLAR:
{context}

Yalnızca yukarıdaki proje belge kaynaklarına dayanarak
güncel kullanıcı sorusunu cevapla.
"""

    client = get_openai_client()

    try:
        response = client.responses.create(
            model=settings.llm_model,

            instructions=(
                GROUNDED_ANSWER_INSTRUCTIONS
            ),

            input=user_input,

            text={
                "format": {
                    "type": "json_schema",
                    "name": "grounded_project_answer",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": [
                                    "answered",
                                    (
                                        "insufficient_"
                                        "evidence"
                                    ),
                                    (
                                        "conflicting_"
                                        "evidence"
                                    ),
                                ],
                            },
                            "answer": {
                                "type": "string",
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "citation_ids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "missing_information": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                            "warnings": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                        },
                        "required": [
                            "status",
                            "answer",
                            "confidence",
                            "citation_ids",
                            "missing_information",
                            "warnings",
                        ],
                    },
                }
            },

            # Yanıt durumunu sonraki konuşmalar
            # için API tarafında saklamıyoruz.
            store=False,
        )

    except Exception as exc:
        raise LlmAnswerError(
            "LLM cevabı oluşturulamadı."
        ) from exc

    try:
        raw_output = response.output_text

        parsed = json.loads(raw_output)

        return LlmGroundedAnswer.model_validate(
            parsed
        )

    except (
        json.JSONDecodeError,
        ValidationError,
    ) as exc:
        raise LlmAnswerError(
            "LLM geçerli cevap formatı döndürmedi."
        ) from exc