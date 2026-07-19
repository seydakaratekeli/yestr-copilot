import re

from supabase import Client

from app.core.config import settings
from app.schemas.search import (
    AskProjectResponse,
    AskProjectSource,
)
from app.services.llm_provider import (
    GroundedAnswer,
    LLMGenerationError,
    LLMProvider,
    LLMSource,
)
from app.services.openai_provider import get_llm_provider
from app.services.rag_context_service import (
    RagSource,
    build_rag_sources,
)
from app.services.semantic_search_service import (
    search_project_chunks,
)


DISCLAIMER = (
    "Bu sonuç ön değerlendirme amaçlıdır ve resmî "
    "YeS-TR sertifikasyon kararı değildir."
)

INSUFFICIENT_EVIDENCE_ANSWER = (
    "Yüklenen belgelerde bu soruyu yanıtlamak için "
    "yeterli kanıt bulunamadı."
)

_CITATION_PATTERN = re.compile(r"\[(S\d+)\]")


def ask_project_question(
    *,
    supabase: Client,
    project_id: str,
    question: str,
    limit: int,
    minimum_similarity: float,
    llm_provider: LLMProvider | None = None,
) -> AskProjectResponse:
    chunks = search_project_chunks(
        supabase=supabase,
        project_id=project_id,
        query=question,
        limit=limit,
        minimum_similarity=minimum_similarity,
    )

    rag_sources = build_rag_sources(
        chunks,
        max_total_characters=(
            settings.rag_max_context_characters
        ),
    )
    response_sources = build_response_sources(
        rag_sources
    )

    if not has_sufficient_evidence(response_sources):
        return _insufficient_evidence_response(
            question=question,
        )

    provider = llm_provider or get_llm_provider()
    llm_sources = [
        LLMSource(
            source_id=source.source_id,
            quote=source.content,
            extraction_method=(
                source.extraction_method
            ),
        )
        for source in rag_sources
    ]

    grounded_answer = provider.generate_grounded_answer(
        question=question,
        sources=llm_sources,
    )

    validate_grounded_answer_sources(
        grounded_answer=grounded_answer,
        sources=response_sources,
    )
    used_sources = [
        source
        for source in response_sources
        if source.citation in grounded_answer.source_ids
    ]

    return AskProjectResponse(
        question=question,
        answer=grounded_answer.answer,
        answer_status=grounded_answer.answer_status,
        has_sufficient_evidence=True,
        disclaimer=DISCLAIMER,
        sources=used_sources,
    )


def build_response_sources(
    sources: list[RagSource],
) -> list[AskProjectSource]:
    return [
        AskProjectSource(
            citation=source.source_id,
            chunk_id=source.chunk_id,
            document_id=source.document_id,
            original_filename=(
                source.original_filename
            ),
            page_number=source.page_number,
            quote=build_short_quote(
                source.content
            ),
            similarity=round(
                source.similarity,
                4,
            ),
            extraction_method=(
                source.extraction_method
            ),
            is_ocr=(
                source.extraction_method == "ocr"
            ),
        )
        for source in sources
        if source.content.strip()
    ]


def build_short_quote(content: str) -> str:
    normalized = " ".join(content.split())
    if not normalized:
        return ""

    max_characters = settings.rag_max_quote_characters

    if len(normalized) <= max_characters:
        return normalized

    return normalized[: max_characters - 3].rstrip() + "..."


def has_sufficient_evidence(
    sources: list[AskProjectSource],
) -> bool:
    return len(sources) >= settings.rag_minimum_source_count


def validate_grounded_answer_sources(
    *,
    grounded_answer: GroundedAnswer,
    sources: list[AskProjectSource],
) -> None:
    available = {
        source.citation
        for source in sources
    }
    declared = set(grounded_answer.source_ids)
    used = set(
        _CITATION_PATTERN.findall(
            grounded_answer.answer
        )
    )

    if not declared:
        raise LLMGenerationError(
            "LLM cevabi kaynak kimligi icermiyor."
        )

    invalid = sorted(declared - available)
    if invalid:
        raise LLMGenerationError(
            "LLM cevabi gecersiz kaynak kimligi iceriyor: "
            + ", ".join(invalid)
        )

    if not used:
        raise LLMGenerationError(
            "LLM cevabi kaynak isareti icermiyor."
        )

    if used != declared:
        raise LLMGenerationError(
            "LLM cevabindaki kaynak isaretleri source_ids "
            "alaniyla eslesmiyor."
        )


def _insufficient_evidence_response(
    *,
    question: str,
) -> AskProjectResponse:
    return AskProjectResponse(
        question=question,
        answer=INSUFFICIENT_EVIDENCE_ANSWER,
        answer_status="insufficient_evidence",
        has_sufficient_evidence=False,
        disclaimer=DISCLAIMER,
        sources=[],
    )
