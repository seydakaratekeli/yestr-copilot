import json

from app.core.config import settings
from app.services.llm_provider import (
    GroundedAnswer,
    LLMConfigurationError,
    LLMGenerationError,
    LLMProvider,
    LLMSource,
    SYSTEM_PROMPT,
    build_grounded_answer_schema,
    build_grounded_answer_prompt,
)


class OpenAIProvider:
    def __init__(self) -> None:
        if not settings.llm_enabled:
            raise LLMConfigurationError(
                "LLM sistemi devre disi. LLM_ENABLED=true olarak ayarlayin."
            )

        if not settings.openai_api_key:
            raise LLMConfigurationError(
                "OpenAI API anahtari backend ortaminda tanimli degil."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError(
                "OpenAI saglayicisi icin openai paketi kurulu degil."
            ) from exc

        self._client = OpenAI(
            api_key=settings.openai_api_key,
        )
        self._model = settings.llm_model

    def generate_grounded_answer(
        self,
        *,
        question: str,
        sources: list[LLMSource],
    ) -> GroundedAnswer:
        prompt = build_grounded_answer_prompt(
            question=question,
            sources=sources,
        )
        source_ids = [
            source.source_id
            for source in sources
        ]
        schema = build_grounded_answer_schema(
            source_ids=source_ids,
        )

        try:
            response = self._client.responses.create(
                model=self._model,
                instructions=SYSTEM_PROMPT,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "yestr_grounded_answer",
                        "schema": schema,
                        "strict": True,
                    }
                },
            )
        except Exception as exc:
            raise LLMGenerationError(
                "LLM cevabi uretilemedi."
            ) from exc

        output_text = getattr(response, "output_text", None)

        if not isinstance(output_text, str) or not output_text.strip():
            raise LLMGenerationError(
                "LLM bos cevap dondurdu."
            )

        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise LLMGenerationError(
                "LLM yapilandirilmis JSON cevabi dondurmedi."
            ) from exc

        answer = parsed.get("answer")
        parsed_source_ids = parsed.get("source_ids")
        answer_status = parsed.get("answer_status")

        if (
            not isinstance(answer, str)
            or not isinstance(parsed_source_ids, list)
            or not all(
                isinstance(source_id, str)
                for source_id in parsed_source_ids
            )
            or answer_status not in {"grounded", "uncertain"}
        ):
            raise LLMGenerationError(
                "LLM cevabi beklenen semaya uymuyor."
            )

        return GroundedAnswer(
            answer=answer.strip(),
            source_ids=parsed_source_ids,
            answer_status=answer_status,
        )


def get_llm_provider() -> LLMProvider:
    if not settings.llm_enabled:
        raise LLMConfigurationError(
            "LLM sistemi devre disi. LLM_ENABLED=true olarak ayarlayin."
        )

    return OpenAIProvider()
