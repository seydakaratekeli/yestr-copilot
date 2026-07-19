from dataclasses import dataclass

from app.services.semantic_search_service import (
    RetrievedChunk,
)


@dataclass(frozen=True)
class RagSource:
    source_id: str

    chunk_id: str
    document_id: str

    original_filename: str
    document_type: str | None

    page_number: int
    similarity: float

    content: str
    extraction_method: str | None


def build_rag_sources(
    chunks: list[RetrievedChunk],
    *,
    max_total_characters: int,
) -> list[RagSource]:
    sources: list[RagSource] = []

    used_characters = 0

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):
        remaining = (
            max_total_characters
            - used_characters
        )

        if remaining <= 0:
            break

        content = chunk.content.strip()

        if not content:
            continue

        if len(content) > remaining:
            content = content[:remaining].rstrip()

        source = RagSource(
            source_id=f"S{index}",
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            original_filename=(
                chunk.original_filename
                or "Bilinmeyen belge"
            ),
            document_type=chunk.document_type,
            page_number=chunk.page_number,
            similarity=chunk.similarity,
            content=content,
            extraction_method=(
                chunk.extraction_method
            ),
        )

        sources.append(source)

        used_characters += len(content)

    return sources


def render_rag_context(
    sources: list[RagSource],
) -> str:
    sections: list[str] = []

    for source in sources:
        sections.append(
            "\n".join(
                [
                    f"[SOURCE_ID: {source.source_id}]",
                    (
                        "DOCUMENT: "
                        f"{source.original_filename}"
                    ),
                    (
                        "DOCUMENT_TYPE: "
                        f"{source.document_type or 'unknown'}"
                    ),
                    f"PAGE: {source.page_number}",
                    (
                        "EXTRACTION_METHOD: "
                        f"{source.extraction_method or 'unknown'}"
                    ),
                    (
                        "SIMILARITY: "
                        f"{source.similarity:.4f}"
                    ),
                    "CONTENT:",
                    source.content,
                ]
            )
        )

    return "\n\n---\n\n".join(sections)
