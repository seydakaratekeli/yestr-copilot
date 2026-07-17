from dataclasses import dataclass

import fitz

from app.core.config import settings
from app.services.ocr_service import (
    OcrError,
    extract_page_text_with_ocr,
)
from app.services.text_service import (
    clean_extracted_text,
    count_words,
)


class PdfExtractionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExtractedBlock:
    block_number: int
    text: str

    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int

    raw_text: str
    cleaned_text: str

    character_count: int
    word_count: int

    extraction_method: str
    extraction_confidence: float | None

    requires_ocr: bool
    ocr_attempted: bool
    ocr_error: str | None

    blocks: list[ExtractedBlock]


def extract_pdf_pages(
    content: bytes,
) -> list[ExtractedPage]:
    try:
        document = fitz.open(
            stream=content,
            filetype="pdf",
        )
    except Exception as exc:
        raise PdfExtractionError(
            "PDF metin çıkarımı için açılamadı."
        ) from exc

    extracted_pages: list[ExtractedPage] = []

    try:
        for page_index in range(
            document.page_count
        ):
            page = document.load_page(page_index)

            native_result = _extract_native_page_text(
                page
            )

            native_text_is_sufficient = (
                native_result.character_count
                >=
                settings
                .ocr_minimum_native_characters
            )

            if native_text_is_sufficient:
                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_index + 1,
                        raw_text=(
                            native_result.raw_text
                        ),
                        cleaned_text=(
                            native_result.cleaned_text
                        ),
                        character_count=(
                            native_result
                            .character_count
                        ),
                        word_count=(
                            native_result.word_count
                        ),
                        extraction_method=(
                            "native_pdf"
                        ),
                        extraction_confidence=1.0,
                        requires_ocr=False,
                        ocr_attempted=False,
                        ocr_error=None,
                        blocks=(
                            native_result.blocks
                        ),
                    )
                )

                continue

            if not settings.ocr_enabled:
                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_index + 1,
                        raw_text=(
                            native_result.raw_text
                        ),
                        cleaned_text=(
                            native_result.cleaned_text
                        ),
                        character_count=(
                            native_result
                            .character_count
                        ),
                        word_count=(
                            native_result.word_count
                        ),
                        extraction_method=(
                            "native_pdf"
                        ),
                        extraction_confidence=0.0,
                        requires_ocr=True,
                        ocr_attempted=False,
                        ocr_error=(
                            "OCR sistemi devre dışı."
                        ),
                        blocks=(
                            native_result.blocks
                        ),
                    )
                )

                continue

            try:
                ocr_result = (
                    extract_page_text_with_ocr(
                        page
                    )
                )

                ocr_successful = (
                    ocr_result.character_count
                    >=
                    settings
                    .ocr_minimum_result_characters
                )

                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_index + 1,
                        raw_text=(
                            ocr_result.raw_text
                        ),
                        cleaned_text=(
                            ocr_result.cleaned_text
                        ),
                        character_count=(
                            ocr_result
                            .character_count
                        ),
                        word_count=(
                            ocr_result.word_count
                        ),
                        extraction_method="ocr",
                        extraction_confidence=(
                            ocr_result.confidence
                        ),
                        requires_ocr=(
                            not ocr_successful
                        ),
                        ocr_attempted=True,
                        ocr_error=(
                            None
                            if ocr_successful
                            else (
                                "OCR sonucunda "
                                "yeterli metin "
                                "bulunamadı."
                            )
                        ),
                        blocks=[],
                    )
                )

            except OcrError as exc:
                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_index + 1,
                        raw_text=(
                            native_result.raw_text
                        ),
                        cleaned_text=(
                            native_result.cleaned_text
                        ),
                        character_count=(
                            native_result
                            .character_count
                        ),
                        word_count=(
                            native_result.word_count
                        ),
                        extraction_method=(
                            "native_pdf"
                        ),
                        extraction_confidence=0.0,
                        requires_ocr=True,
                        ocr_attempted=True,
                        ocr_error=str(exc),
                        blocks=(
                            native_result.blocks
                        ),
                    )
                )

        return extracted_pages

    finally:
        document.close()


@dataclass(frozen=True)
class NativePageExtraction:
    raw_text: str
    cleaned_text: str
    character_count: int
    word_count: int
    blocks: list[ExtractedBlock]


def _extract_native_page_text(
    page: fitz.Page,
) -> NativePageExtraction:
    raw_blocks = page.get_text(
        "blocks",
        sort=True,
    )

    blocks: list[ExtractedBlock] = []

    for raw_block in raw_blocks:
        if len(raw_block) < 7:
            continue

        x0, y0, x1, y1 = map(
            float,
            raw_block[:4],
        )

        block_text = str(
            raw_block[4]
        ).strip()

        block_number = int(
            raw_block[5]
        )

        block_type = int(
            raw_block[6]
        )

        if block_type != 0:
            continue

        cleaned_block_text = (
            clean_extracted_text(
                block_text
            )
        )

        if not cleaned_block_text:
            continue

        blocks.append(
            ExtractedBlock(
                block_number=block_number,
                text=cleaned_block_text,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
            )
        )

    raw_text = "\n\n".join(
        block.text
        for block in blocks
    )

    cleaned_text = clean_extracted_text(
        raw_text
    )

    return NativePageExtraction(
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        character_count=len(cleaned_text),
        word_count=count_words(cleaned_text),
        blocks=blocks,
    )