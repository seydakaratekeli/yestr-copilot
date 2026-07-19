from app.schemas.answer import AnswerCitation
from app.schemas.llm_answer import (
    LlmGroundedAnswer,
)
from app.services.rag_context_service import (
    RagSource,
)


def validate_and_build_citations(
    *,
    llm_answer: LlmGroundedAnswer,
    sources: list[RagSource],
) -> list[AnswerCitation]:
    source_map = {
        source.source_id: source
        for source in sources
    }

    citations: list[AnswerCitation] = []

    seen_source_ids: set[str] = set()

    for source_id in llm_answer.citation_ids:
        if source_id in seen_source_ids:
            continue

        source = source_map.get(source_id)

        # Modelin uydurduğu kaynak ID’sini
        # cevaba dahil etmiyoruz.
        if source is None:
            continue

        seen_source_ids.add(source_id)

        citations.append(
            AnswerCitation(
                source_id=source.source_id,
                document_id=source.document_id,
                original_filename=(
                    source.original_filename
                ),
                page_number=(
                    source.page_number
                ),
                document_type=(
                    source.document_type
                ),
                similarity=round(
                    source.similarity,
                    4,
                ),
                excerpt=_build_excerpt(
                    source.content
                ),
            )
        )

    return citations


def _build_excerpt(
    content: str,
    maximum_length: int = 500,
) -> str:
    normalized = " ".join(
        content.split()
    )

    if len(normalized) <= maximum_length:
        return normalized

    return (
        normalized[:maximum_length].rstrip()
        + "..."
    )