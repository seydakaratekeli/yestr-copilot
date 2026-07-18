from dataclasses import dataclass

import fitz


class InvalidPdfError(ValueError):
    pass


@dataclass(frozen=True)
class PdfMetadata:
    page_count: int
    has_extractable_text: bool
    extracted_character_count: int
    requires_ocr: bool


def inspect_pdf(
    file_content: bytes,
    *,
    max_page_count: int | None = None,
) -> PdfMetadata:
    if not file_content:
        raise InvalidPdfError("PDF dosyası boş.")

    # PDF dosyaları genellikle %PDF imzasıyla başlar.
    # Tek başına yeterli doğrulama değildir; asıl kontrolü PyMuPDF yapar.
    if not file_content.startswith(b"%PDF"):
        raise InvalidPdfError(
            "Dosya PDF imzasına sahip değil."
        )

    try:
        document = fitz.open(
            stream=file_content,
            filetype="pdf",
        )
    except Exception as exc:
        raise InvalidPdfError(
            "Dosya geçerli veya okunabilir bir PDF değil."
        ) from exc

    try:
        if document.page_count == 0:
            raise InvalidPdfError(
                "PDF içerisinde sayfa bulunamadı."
            )

        if (
            max_page_count is not None
            and document.page_count > max_page_count
        ):
            raise InvalidPdfError(
                f"PDF en fazla {max_page_count} sayfa olabilir."
            )

        extracted_character_count = 0

        # MVP'de tüm belgeyi çıkarmak yerine ilk 5 sayfayı
        # örnekleyerek OCR gereksinimini tahmin ediyoruz.
        sampled_page_count = min(document.page_count, 5)

        for page_index in range(sampled_page_count):
            page = document.load_page(page_index)
            page_text = str(page.get_text("text")).strip()

            extracted_character_count += len(page_text)

        has_extractable_text = (
            extracted_character_count >= 50
        )

        return PdfMetadata(
            page_count=document.page_count,
            has_extractable_text=has_extractable_text,
            extracted_character_count=(
                extracted_character_count
            ),
            requires_ocr=not has_extractable_text,
        )

    finally:
        document.close()