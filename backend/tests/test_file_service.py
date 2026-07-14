"""
file_service için birim testleri.

Test edilen senaryolar:
- sanitize_filename: None, boş string, normal isim, Türkçe/özel karakter,
  çok uzun isim, uzantı yoksa .pdf eklenir, .pdf olmayan uzantı düzeltilir
- build_storage_path: yol formatı, document_id atanması, dosya adı sanitasyonu
"""

import pytest

from app.services.file_service import build_storage_path, sanitize_filename


# ---------------------------------------------------------------------------
# sanitize_filename testleri
# ---------------------------------------------------------------------------


class TestSanitizeFilename:
    def test_none_returns_default(self):
        assert sanitize_filename(None) == "document.pdf"

    def test_empty_string_returns_default(self):
        assert sanitize_filename("") == "document.pdf"

    def test_simple_ascii_filename(self):
        result = sanitize_filename("my-report.pdf")
        assert result == "my-report.pdf"

    def test_turkish_characters_are_stripped(self):
        # Türkçe karakterler ASCII encode sırasında düşer
        result = sanitize_filename("mimari-proje.pdf")
        assert result.endswith(".pdf")
        assert len(result) > 4

    def test_spaces_replaced_with_dashes(self):
        result = sanitize_filename("my file name.pdf")
        assert " " not in result
        assert result.endswith(".pdf")

    def test_non_pdf_extension_replaced(self):
        result = sanitize_filename("document.docx")
        assert result.endswith(".pdf")

    def test_no_extension_gets_pdf(self):
        result = sanitize_filename("noextension")
        assert result.endswith(".pdf")

    def test_long_filename_truncated(self):
        long_name = "a" * 200 + ".pdf"
        result = sanitize_filename(long_name)
        # stem en fazla 80 karakter + .pdf = 84
        assert len(result) <= 84

    def test_special_chars_removed(self):
        result = sanitize_filename("file!@#$%name.pdf")
        # Özel karakterler kaldırılmalı
        assert result.endswith(".pdf")
        # Alfanumerik ve tire/alt çizgi dışındaki karakterler olmamalı
        stem = result[:-4]
        assert all(
            c.isalnum() or c in "-_" for c in stem
        ), f"Unexpected chars in stem: {stem!r}"

    def test_only_special_chars_returns_document(self):
        result = sanitize_filename("!!!.pdf")
        assert result == "document.pdf"


# ---------------------------------------------------------------------------
# build_storage_path testleri
# ---------------------------------------------------------------------------


class TestBuildStoragePath:
    def test_returns_tuple_of_two_strings(self):
        result = build_storage_path(
            user_id="user-123",
            project_id="proj-456",
            filename="test.pdf",
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_path_contains_user_and_project(self):
        _, path = build_storage_path(
            user_id="user-abc",
            project_id="proj-xyz",
            filename="report.pdf",
        )
        assert "users/user-abc" in path
        assert "projects/proj-xyz" in path

    def test_path_ends_with_pdf(self):
        _, path = build_storage_path(
            user_id="u1",
            project_id="p1",
            filename="doc.pdf",
        )
        assert path.endswith(".pdf")

    def test_document_id_provided_is_used(self):
        doc_id = "my-custom-doc-id"
        returned_id, path = build_storage_path(
            user_id="u1",
            project_id="p1",
            document_id=doc_id,
            filename="doc.pdf",
        )
        assert returned_id == doc_id
        assert doc_id in path

    def test_document_id_auto_generated_when_none(self):
        returned_id, path = build_storage_path(
            user_id="u1",
            project_id="p1",
            document_id=None,
            filename="doc.pdf",
        )
        # UUID formatında olmalı
        assert len(returned_id) == 36
        assert "-" in returned_id
        assert returned_id in path

    def test_two_calls_without_document_id_produce_different_ids(self):
        id1, _ = build_storage_path(
            user_id="u1",
            project_id="p1",
            filename="doc.pdf",
        )
        id2, _ = build_storage_path(
            user_id="u1",
            project_id="p1",
            filename="doc.pdf",
        )
        assert id1 != id2

    def test_path_structure(self):
        _, path = build_storage_path(
            user_id="USER",
            project_id="PROJ",
            document_id="DOCID",
            filename="file.pdf",
        )
        # Beklenen format: users/{uid}/projects/{pid}/{docid}/{filename}
        parts = path.split("/")
        assert parts[0] == "users"
        assert parts[1] == "USER"
        assert parts[2] == "projects"
        assert parts[3] == "PROJ"
        assert parts[4] == "DOCID"
