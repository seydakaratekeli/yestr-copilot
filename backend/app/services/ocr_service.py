from dataclasses import dataclass
from pathlib import Path

import fitz

from app.core.config import settings
from app.services.text_service import (
    clean_extracted_text,
    count_words,
)


class OcrError(RuntimeError):
    pass


@dataclass(frozen=True)
class OcrResult:
    raw_text: str
    cleaned_text: str
    character_count: int
    word_count: int
    language: str
    confidence: float | None


def validate_ocr_configuration() -> None:
    if not settings.ocr_enabled:
        return

    if not settings.tessdata_path:
        raise OcrError(
            "TESSDATA_PATH ayarı tanımlanmamış."
        )

    tessdata_directory = Path(
        settings.tessdata_path
    )

    if not tessdata_directory.exists():
        raise OcrError(
            "Tesseract tessdata klasörü bulunamadı: "
            f"{tessdata_directory}"
        )

    languages = settings.ocr_languages.split("+")

    missing_languages: list[str] = []

    for language in languages:
        language_file = (
            tessdata_directory /
            f"{language}.traineddata"
        )

        if not language_file.exists():
            missing_languages.append(language)

    if missing_languages:
        raise OcrError(
            "Eksik Tesseract dil dosyaları: "
            + ", ".join(missing_languages)
        )


def extract_page_text_with_ocr(
    page: fitz.Page,
) -> OcrResult:
    if not settings.ocr_enabled:
        raise OcrError(
            "OCR sistemi devre dışı."
        )

    validate_ocr_configuration()

    try:
        text_page = page.get_textpage_ocr(
            language=settings.ocr_languages,
            dpi=settings.ocr_dpi,
            full=True,
            tessdata=settings.tessdata_path,
        )

        raw_text = page.get_text(
            "text",
            textpage=text_page,
            sort=False,
        ).strip()

    except Exception as exc:
        raise OcrError(
            "Sayfa OCR işlemi gerçekleştirilemedi. "
            "Tesseract dil verilerini ve "
            "TESSDATA_PATH ayarını kontrol edin."
        ) from exc

    cleaned_text = clean_extracted_text(
        raw_text
    )

    if (
        len(cleaned_text)
        < settings.ocr_minimum_result_characters
    ):
        return OcrResult(
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            character_count=len(cleaned_text),
            word_count=count_words(cleaned_text),
            language=settings.ocr_languages,
            confidence=None,
        )

    return OcrResult(
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        character_count=len(cleaned_text),
        word_count=count_words(cleaned_text),
        language=settings.ocr_languages,
        confidence=None,
    )