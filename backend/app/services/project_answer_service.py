from supabase import Client

from app.core.config import settings
from app.schemas.answer import (
    ProjectQuestionResponse,
)
from app.services.answer_guard_service import (
    apply_answer_guards,
)
from app.services.citation_service import (
    validate_and_build_citations,
)
from app.services.llm_answer_service import (
    generate_grounded_answer,
)
from app.services.rag_context_service import (
    build_rag_sources,
)
from app.services.semantic_search_service import (
    search_project_chunks,
)


def answer_project_question(
    *,
    supabase: Client,
    project_id: str,
    question: str,
    search_limit: int | None = None,
    minimum_similarity: float | None = None,
) -> ProjectQuestionResponse:
    final_search_limit = (
        search_limit
        or settings.rag_search_limit
    )

    final_minimum_similarity = (
        minimum_similarity
        if minimum_similarity is not None
        else settings.rag_minimum_similarity
    )

    chunks = search_project_chunks(
        supabase=supabase,
        project_id=project_id,
        query=question,
        limit=final_search_limit,
        minimum_similarity=(
            final_minimum_similarity
        ),
    )

    sources = build_rag_sources(
        chunks,
        max_total_characters=(
            settings
            .rag_max_context_characters
        ),
    )

    llm_answer = generate_grounded_answer(
        question=question,
        sources=sources,
    )

    citations = validate_and_build_citations(
        llm_answer=llm_answer,
        sources=sources,
    )

    guarded_answer = apply_answer_guards(
        answer=llm_answer,
        citations=citations,
    )

    # Guard sonrasında citation ID listesi
    # değişebileceği için tekrar filtreliyoruz.
    valid_ids = set(
        guarded_answer.citation_ids
    )

    final_citations = [
        citation
        for citation in citations
        if citation.source_id in valid_ids
    ]

    return ProjectQuestionResponse(
        question=question,
        status=guarded_answer.status,
        answer=guarded_answer.answer,
        confidence=guarded_answer.confidence,
        citations=final_citations,
        missing_information=(
            guarded_answer
            .missing_information
        ),
        warnings=guarded_answer.warnings,
        retrieved_source_count=len(sources),
    )