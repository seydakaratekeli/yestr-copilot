"""
document upload endpoint için entegrasyon testleri.

Gerçek Supabase yerine mock'lar kullanılır. Test edilen senaryolar:

1. Kimlik doğrulama olmadan 401 döner
2. Dosya gönderilmezse 422 döner (FastAPI zorunlu alan)
3. Dosya sayısı sınırı aşılırsa 400 döner
4. Dosya sayısı ile document_types sayısı eşleşmezse 400 döner
5. Geçersiz document_type gönderilirse 422 döner
6. PDF olmayan content-type ile dosya gönderilirse başarısız listesine eklenir
7. Boyut sınırını aşan PDF başarısız listesine eklenir
8. Geçerli iki PDF başarıyla yüklenir → 201, successful listesi dolu, failed boş
9. Başarılı yanıtta doğru alanlar döner (filename, page_count, ocr flags…)
10. Metin içeren PDF → requires_ocr=False, extraction_status=completed
11. Metin içermeyen PDF → requires_ocr=True, extraction_status=pending
12. Kısmen başarılı yükleme (1 başarılı, 1 başarısız) → 201, her iki liste dolu
13. Tüm geçerli belge türleri kabul edilir
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

# endpoint'in tam URL'si:  /api prefix + documents router prefix + route path
# router.py: api_router.include_router(documents_router, prefix="/documents")
# documents.py: @router.post("/projects/{project_id}/documents")
# → /api/documents/projects/{project_id}/documents
ENDPOINT = "/api/projects/{project_id}/documents"

FAKE_USER_ID = "user-test-123"
FAKE_USER_EMAIL = "test@example.com"
FAKE_PROJECT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _url(project_id: str = FAKE_PROJECT_ID) -> str:
    return ENDPOINT.format(project_id=project_id)


def _auth_headers() -> dict:
    return {"Authorization": "Bearer fake-token"}


def _make_pdf_bytes(text: str = "Test içeriği. " * 20) -> bytes:
    """Gerçek, PyMuPDF ile okunabilir minimal PDF baytı üretir."""
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    if text:
        page.insert_text((72, 72), text, fontsize=12)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_auth():
    """get_current_user dependency'yi FastAPI dependency_overrides ile bypass eder."""
    from app.core.auth import AuthenticatedUser, get_current_user

    fake_user = AuthenticatedUser(
        id=FAKE_USER_ID, email=FAKE_USER_EMAIL
    )

    async def _override():
        return fake_user

    app.dependency_overrides[get_current_user] = _override
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def mock_supabase():
    """get_supabase_admin'i mock Supabase istemcisiyle değiştirir."""
    mock = MagicMock()

    # DB insert başarılı
    mock.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "doc-id-placeholder"}
    ]
    # Status update başarılı
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value = (
        MagicMock()
    )
    # Storage upload başarılı
    mock.storage.from_.return_value.upload.return_value = MagicMock()

    with patch(
        "app.api.routes.documents.get_supabase_admin",
        return_value=mock,
    ):
        yield mock


@pytest.fixture
def mock_project_access():
    """get_accessible_project'i her zaman geçer şekilde mock'lar."""
    with patch(
        "app.api.routes.documents.get_accessible_project",
        return_value={"id": FAKE_PROJECT_ID, "created_by": FAKE_USER_ID},
    ) as m:
        yield m


@pytest.fixture
def mock_storage_upload():
    """upload_pdf_to_storage'i başarılı şekilde mock'lar."""
    with patch(
        "app.api.routes.documents.upload_pdf_to_storage",
        return_value=None,
    ) as m:
        yield m


@pytest.fixture
def client(
    mock_auth,
    mock_supabase,
    mock_project_access,
    mock_storage_upload,
):
    """Tüm dış bağımlılıkları mock'lanmış tam test istemcisi."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# 1. Kimlik doğrulama
# ---------------------------------------------------------------------------


class TestDocumentUploadAuth:
    def test_no_auth_returns_401(self):
        """Gerçek get_current_user dependency → token yoksa 401."""
        with TestClient(app) as c:
            response = c.post(
                _url(),
                files=[
                    ("files", ("test.pdf", b"%PDF-1.4", "application/pdf"))
                ],
                data={"document_types": ["other"]},
            )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# 2-5. Validasyon hataları
# ---------------------------------------------------------------------------


class TestDocumentUploadValidation:
    def test_no_files_returns_422(self, client):
        """files field zorunlu → FastAPI 422 döner."""
        response = client.post(
            _url(),
            headers=_auth_headers(),
            data={"document_types": ["other"]},
        )
        assert response.status_code == 422

    def test_too_many_files_returns_400(self, client):
        """11 dosya → max_files_per_request (10) aşıldı → 400."""
        pdf = _make_pdf_bytes()
        files = [
            ("files", (f"doc{i}.pdf", pdf, "application/pdf"))
            for i in range(11)
        ]
        data = {"document_types": ["other"] * 11}

        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=files,
            data=data,
        )
        assert response.status_code == 400
        assert "10" in response.json()["detail"]

    def test_mismatched_document_types_returns_400(self, client):
        """2 dosya, 1 document_type → eşleşme yok → 400."""
        pdf = _make_pdf_bytes()
        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[
                ("files", ("a.pdf", pdf, "application/pdf")),
                ("files", ("b.pdf", pdf, "application/pdf")),
            ],
            data={"document_types": ["other"]},
        )
        assert response.status_code == 400

    def test_invalid_document_type_returns_422(self, client):
        """Bilinmeyen document_type → 422."""
        pdf = _make_pdf_bytes()
        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[("files", ("a.pdf", pdf, "application/pdf"))],
            data={"document_types": ["invalid_type_xyz"]},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 6-7. Per-dosya hatalar (failed listesi)
# ---------------------------------------------------------------------------


class TestDocumentUploadFileErrors:
    def test_non_pdf_content_type_goes_to_failed(self, client):
        """image/jpeg content-type → 201 ama failed listesinde."""
        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[
                (
                    "files",
                    ("image.jpg", b"fake-image-content", "image/jpeg"),
                )
            ],
            data={"document_types": ["other"]},
        )
        assert response.status_code == 201
        body = response.json()
        assert len(body["failed"]) == 1
        assert len(body["successful"]) == 0

    def test_oversized_file_goes_to_failed(self, client):
        """26 MB'lık içerik (limit 25 MB) → 201 ama failed listesinde."""
        oversized = b"%PDF-1.4 " + b"X" * (26 * 1024 * 1024)
        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[("files", ("big.pdf", oversized, "application/pdf"))],
            data={"document_types": ["other"]},
        )
        assert response.status_code == 201
        body = response.json()
        assert len(body["failed"]) == 1
        assert len(body["successful"]) == 0


# ---------------------------------------------------------------------------
# 8-13. Başarılı senaryolar
# ---------------------------------------------------------------------------


class TestDocumentUploadSuccess:
    def test_two_valid_pdfs_both_succeed(self, client, mock_supabase):
        """2 geçerli PDF → 201, her ikisi successful listesinde."""
        pdf = _make_pdf_bytes("Bu bir test belgesidir. " * 10)

        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[
                ("files", ("first.pdf", pdf, "application/pdf")),
                ("files", ("second.pdf", pdf, "application/pdf")),
            ],
            data={"document_types": ["floor_plan", "energy_report"]},
        )

        assert response.status_code == 201
        body = response.json()
        assert len(body["successful"]) == 2
        assert len(body["failed"]) == 0

    def test_successful_response_has_correct_fields(self, client):
        """Başarılı yanıt tüm beklenen alanları içermeli."""
        pdf = _make_pdf_bytes("Örnek belge içeriği. " * 10)

        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[("files", ("report.pdf", pdf, "application/pdf"))],
            data={"document_types": ["technical_specification"]},
        )

        assert response.status_code == 201
        body = response.json()
        doc = body["successful"][0]

        assert doc["original_filename"] == "report.pdf"
        assert doc["document_type"] == "technical_specification"
        assert doc["file_size_bytes"] > 0
        assert doc["page_count"] >= 1
        assert "id" in doc
        assert "requires_ocr" in doc
        assert "has_extractable_text" in doc
        assert "processing_status" in doc
        assert "extraction_status" in doc

    def test_text_pdf_has_correct_ocr_flags(self, client):
        """Metin dolu PDF → requires_ocr=False, extraction_status=completed."""
        pdf = _make_pdf_bytes("Bu belge içinde metin var. " * 20)

        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[("files", ("textual.pdf", pdf, "application/pdf"))],
            data={"document_types": ["other"]},
        )

        body = response.json()
        doc = body["successful"][0]
        assert doc["requires_ocr"] is False
        assert doc["has_extractable_text"] is True
        assert doc["extraction_status"] == "completed"

    def test_image_only_pdf_requires_ocr(self, client):
        """Metin içermeyen boş sayfalı PDF → requires_ocr=True, extraction_status=pending."""
        import fitz

        doc_fitz = fitz.open()
        doc_fitz.new_page(width=595, height=842)
        buf = io.BytesIO()
        doc_fitz.save(buf)
        doc_fitz.close()
        pdf = buf.getvalue()

        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[("files", ("scan.pdf", pdf, "application/pdf"))],
            data={"document_types": ["site_plan"]},
        )

        body = response.json()
        doc = body["successful"][0]
        assert doc["requires_ocr"] is True
        assert doc["extraction_status"] == "pending"

    def test_partial_success_one_valid_one_invalid(self, client):
        """1 geçerli + 1 geçersiz → her iki listede 1 kayıt."""
        valid_pdf = _make_pdf_bytes("Geçerli belge içeriği. " * 10)
        invalid_content = b"this is not a pdf at all"

        response = client.post(
            _url(),
            headers=_auth_headers(),
            files=[
                ("files", ("valid.pdf", valid_pdf, "application/pdf")),
                ("files", ("invalid.pdf", invalid_content, "application/pdf")),
            ],
            data={"document_types": ["other", "other"]},
        )

        assert response.status_code == 201
        body = response.json()
        assert len(body["successful"]) == 1
        assert len(body["failed"]) == 1
        failed_names = [f["original_filename"] for f in body["failed"]]
        assert "invalid.pdf" in failed_names

    def test_all_document_types_accepted(self, client):
        """Her geçerli belge türü için 201 dönmeli."""
        pdf = _make_pdf_bytes("Test. " * 20)

        allowed_types = [
            "site_plan",
            "floor_plan",
            "section",
            "facade",
            "energy_report",
            "technical_specification",
            "product_datasheet",
            "mechanical_report",
            "electrical_report",
            "other",
        ]

        for doc_type in allowed_types:
            response = client.post(
                _url(),
                headers=_auth_headers(),
                files=[("files", ("doc.pdf", pdf, "application/pdf"))],
                data={"document_types": [doc_type]},
            )
            assert response.status_code == 201, (
                f"Tür '{doc_type}' için 201 beklendi, {response.status_code} geldi"
            )
