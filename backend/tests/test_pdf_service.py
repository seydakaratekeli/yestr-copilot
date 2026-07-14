"""
pdf_service için birim testleri.

Test edilen senaryolar:
- Boş içerik → InvalidPdfError
- PDF imzası olmayan içerik → InvalidPdfError
- Bozuk / okunaksız PDF → InvalidPdfError
- Sıfır sayfalı PDF → InvalidPdfError
- Sayfa sayısı sınırı aşıldığında → InvalidPdfError
- Geçerli, metin içeren PDF → PdfMetadata (requires_ocr=False)
- Geçerli, metin içermeyen (taranmış) PDF → PdfMetadata (requires_ocr=True)
"""

import io
import struct

import pytest

from app.services.pdf_service import InvalidPdfError, PdfMetadata, inspect_pdf


# ---------------------------------------------------------------------------
# Test yardımcıları
# ---------------------------------------------------------------------------


def _minimal_pdf(text: str = "") -> bytes:
    """
    PyMuPDF tarafından okunabilecek minimum geçerli bir PDF baytı üretir.
    Tek sayfa, isteğe bağlı metin bloğu içerir.
    """
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    if text:
        page.insert_text(
            (72, 72),
            text,
            fontsize=12,
        )

    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _multi_page_pdf(page_count: int, text_per_page: str = "") -> bytes:
    """Belirtilen sayfa sayısında geçerli PDF üretir."""
    import fitz

    doc = fitz.open()
    for _ in range(page_count):
        page = doc.new_page(width=595, height=842)
        if text_per_page:
            page.insert_text((72, 72), text_per_page, fontsize=12)

    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Hata senaryoları
# ---------------------------------------------------------------------------


class TestInspectPdfErrors:
    def test_empty_content_raises(self):
        with pytest.raises(InvalidPdfError, match="boş"):
            inspect_pdf(b"")

    def test_non_pdf_signature_raises(self):
        with pytest.raises(InvalidPdfError, match="imza"):
            inspect_pdf(b"This is not a PDF at all")

    def test_corrupted_pdf_raises(self):
        # %PDF imzasıyla başlayıp sonrası çöp
        with pytest.raises(InvalidPdfError):
            inspect_pdf(b"%PDF-1.4 CORRUPTED_GARBAGE")

    def test_page_count_limit_exceeded(self):
        # 5 sayfalık PDF, limit 3 → hata
        content = _multi_page_pdf(page_count=5)
        with pytest.raises(InvalidPdfError, match="sayfa"):
            inspect_pdf(content, max_page_count=3)

    def test_exact_page_limit_is_allowed(self):
        # 3 sayfalık PDF, limit 3 → hata olmamalı
        content = _multi_page_pdf(page_count=3, text_per_page="A" * 100)
        result = inspect_pdf(content, max_page_count=3)
        assert result.page_count == 3


# ---------------------------------------------------------------------------
# Başarılı senaryolar
# ---------------------------------------------------------------------------


class TestInspectPdfSuccess:
    def test_returns_pdf_metadata_type(self):
        content = _minimal_pdf(text="Merhaba dünya, bu bir test belgesidir.")
        result = inspect_pdf(content)
        assert isinstance(result, PdfMetadata)

    def test_page_count_is_correct(self):
        content = _multi_page_pdf(page_count=2, text_per_page="Sayfa içeriği.")
        result = inspect_pdf(content)
        assert result.page_count == 2

    def test_text_rich_pdf_does_not_require_ocr(self):
        # Yeterince metin → has_extractable_text=True, requires_ocr=False
        long_text = "Bu bir test cümlesidir. " * 20  # >50 karakter
        content = _minimal_pdf(text=long_text)
        result = inspect_pdf(content)
        assert result.has_extractable_text is True
        assert result.requires_ocr is False
        assert result.extracted_character_count >= 50

    def test_empty_text_pdf_requires_ocr(self):
        # Metin eklenmemiş boş sayfa → taranmış görüntü gibi davranır
        content = _minimal_pdf(text="")
        result = inspect_pdf(content)
        assert result.has_extractable_text is False
        assert result.requires_ocr is True

    def test_sparse_text_below_threshold_requires_ocr(self):
        # 50 karakterin altında metin → OCR gerekli
        content = _minimal_pdf(text="Az")  # < 50 karakter
        result = inspect_pdf(content)
        assert result.requires_ocr is True

    def test_no_page_limit_by_default(self):
        # max_page_count=None olduğunda limitsiz çalışmalı
        content = _multi_page_pdf(page_count=10, text_per_page="Test.")
        result = inspect_pdf(content)
        assert result.page_count == 10

    def test_extracted_character_count_is_non_negative(self):
        content = _minimal_pdf(text="")
        result = inspect_pdf(content)
        assert result.extracted_character_count >= 0

    def test_single_page_pdf(self):
        content = _minimal_pdf(text="Tek sayfa içeriği. " * 5)
        result = inspect_pdf(content)
        assert result.page_count == 1
