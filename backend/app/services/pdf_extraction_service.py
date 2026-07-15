from dataclasses import dataclass

import fitz

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

    requires_ocr: bool

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

                # PyMuPDF’de block_type 0 metin,
                # 1 görüntü bloğudur.
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

            character_count = len(
                cleaned_text
            )

            word_count = count_words(
                cleaned_text
            )

            requires_ocr = (
                character_count < 30
            )

            extracted_pages.append(
                ExtractedPage(
                    page_number=page_index + 1,
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    character_count=character_count,
                    word_count=word_count,
                    requires_ocr=requires_ocr,
                    blocks=blocks,
                )
            )

        return extracted_pages

    finally:
        document.close()