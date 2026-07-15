from dataclasses import dataclass

from app.services.text_service import count_words


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str
    character_count: int
    word_count: int


def split_text_into_chunks(
    text: str,
    *,
    chunk_size: int,
    overlap: int,
    minimum_chunk_size: int,
) -> list[TextChunk]:
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "Chunk boyutu sıfırdan büyük olmalıdır."
        )

    if overlap < 0:
        raise ValueError(
            "Overlap negatif olamaz."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "Overlap chunk boyutundan küçük olmalıdır."
        )

    chunks: list[TextChunk] = []
    text_length = len(text)

    start = 0
    chunk_index = 0

    while start < text_length:
        target_end = min(
            start + chunk_size,
            text_length,
        )

        end = _find_natural_break(
            text=text,
            start=start,
            target_end=target_end,
        )

        content = text[start:end].strip()

        if (
            content
            and (
                len(content) >= minimum_chunk_size
                or not chunks
                or end == text_length
            )
        ):
            chunks.append(
                TextChunk(
                    index=chunk_index,
                    content=content,
                    character_count=len(content),
                    word_count=count_words(content),
                )
            )

            chunk_index += 1

        if end >= text_length:
            break

        next_start = max(
            end - overlap,
            start + 1,
        )

        start = _move_to_word_boundary(
            text,
            next_start,
        )

    return chunks


def _find_natural_break(
    *,
    text: str,
    start: int,
    target_end: int,
) -> int:
    if target_end >= len(text):
        return len(text)

    minimum_search_position = start + int(
        (target_end - start) * 0.65
    )

    candidate_separators = [
        "\n\n",
        "\n",
        ". ",
        "? ",
        "! ",
        "; ",
        ", ",
        " ",
    ]

    for separator in candidate_separators:
        position = text.rfind(
            separator,
            minimum_search_position,
            target_end,
        )

        if position != -1:
            return position + len(separator)

    return target_end


def _move_to_word_boundary(
    text: str,
    position: int,
) -> int:
    while (
        position < len(text)
        and position > 0
        and not text[position - 1].isspace()
    ):
        position += 1

    return min(position, len(text))