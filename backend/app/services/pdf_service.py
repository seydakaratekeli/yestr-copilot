from dataclasses import dataclass
from io import BytesIO

import fitz


class InvalidPdfError(ValueError):
    pass


@dataclass
class PdfMetadata:
    page_count: int
    has_extractable_text: bool


def inspect_pdf(file_content: bytes) -> PdfMetadata:
    if not file_content:
        raise InvalidPdfError("PDF dosyası boş.")

    try:
        document = fitz.open(
            stream=BytesIO(file_content),
            filetype="pdf",
        )
    except Exception as exc:
        raise InvalidPdfError(
            "Dosya geçerli bir PDF değil."
        ) from exc

    if document.page_count == 0:
        document.close()
        raise InvalidPdfError("PDF içerisinde sayfa bulunamadı.")

    has_extractable_text = False

    sample_page_count = min(document.page_count, 5)

    for page_index in range(sample_page_count):
        text = document[page_index].get_text("text").strip()

        if len(text) >= 20:
            has_extractable_text = True
            break

    metadata = PdfMetadata(
        page_count=document.page_count,
        has_extractable_text=has_extractable_text,
    )

    document.close()

    return metadata