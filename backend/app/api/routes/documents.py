from uuid import UUID, uuid4
from fastapi import BackgroundTasks

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.core.auth import (
    AuthenticatedUser,
    get_current_user,
)
from app.core.config import settings
from app.core.supabase import get_supabase_admin
from app.schemas.document import (
    DocumentUploadFailure,
    DocumentUploadResult,
    MultipleDocumentUploadResponse,
)
from app.services.file_service import (
    build_storage_path,
)
from app.services.pdf_service import (
    InvalidPdfError,
    inspect_pdf,
)
from app.services.project_access_service import (
    get_accessible_project,
)
from app.services.storage_service import (
    StorageUploadError,
    remove_file_from_storage,
    upload_pdf_to_storage,
)
from app.services.document_processing_service import (
    process_document,
)

router = APIRouter()


ALLOWED_DOCUMENT_TYPES = {
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
}


@router.post(
    "/projects/{project_id}/documents",
    response_model=MultipleDocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_project_documents(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    document_types: list[str] = Form(...),
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> MultipleDocumentUploadResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="En az bir PDF seçilmelidir.",
        )

    if len(files) > settings.max_files_per_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Tek istekte en fazla "
                f"{settings.max_files_per_request} "
                "dosya yüklenebilir."
            ),
        )

    if len(files) != len(document_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Her dosya için bir belge türü "
                "gönderilmelidir."
            ),
        )

    invalid_document_types = [
        document_type
        for document_type in document_types
        if document_type not in ALLOWED_DOCUMENT_TYPES
    ]

    if invalid_document_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Geçersiz belge türü gönderildi.",
        )

    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    successful: list[DocumentUploadResult] = []
    failed: list[DocumentUploadFailure] = []

    for file, document_type in zip(
        files,
        document_types,
        strict=True,
    ):
        original_filename = (
            file.filename or "document.pdf"
        )

        storage_path: str | None = None

        try:
            if file.content_type not in {
                "application/pdf",
                "application/x-pdf",
            }:
                raise InvalidPdfError(
                    "Yalnızca PDF dosyaları kabul edilir."
                )

            content = await file.read()

            if len(content) > settings.max_pdf_size_bytes:
                raise InvalidPdfError(
                    "Dosya boyutu en fazla "
                    f"{settings.max_pdf_size_mb} MB "
                    "olabilir."
                )

            metadata = inspect_pdf(
                content,
                max_page_count=(
                    settings.max_pdf_page_count
                ),
            )

            document_id = str(uuid4())

            _, storage_path = build_storage_path(
                user_id=current_user.id,
                project_id=str(project_id),
                document_id=document_id,
                filename=original_filename,
            )

            upload_pdf_to_storage(
                supabase=supabase,
                bucket=settings.storage_bucket,
                storage_path=storage_path,
                content=content,
            )

            extraction_status = (
                "pending"
                if metadata.requires_ocr
                else "completed"
            )

            insert_response = (
                supabase
                .table("project_documents")
                .insert(
                    {
                        "id": document_id,
                        "project_id": str(project_id),
                        "uploaded_by": current_user.id,
                        "original_filename": (
                            original_filename
                        ),
                        "storage_path": storage_path,
                        "document_type": document_type,
                        "mime_type": "application/pdf",
                        "file_size_bytes": len(content),
                        "page_count": (
                            metadata.page_count
                        ),
                        "processing_status": (
                            "queued"
                        ),
                        "extraction_status": (
                            "pending"
                        ),
                        "error_message": None,
                    }
                )
                .execute()
            )

            if not insert_response.data:
                raise RuntimeError(
                    "Belge veritabanına kaydedilemedi."
                )

            background_tasks.add_task(
                process_document,
                document_id=document_id,
            )


            successful.append(
                DocumentUploadResult(
                    id=document_id,
                    original_filename=(
                        original_filename
                    ),
                    document_type=document_type,
                    file_size_bytes=len(content),
                    page_count=metadata.page_count,
                    has_extractable_text=(
                        metadata.has_extractable_text
                    ),
                    requires_ocr=(
                        metadata.requires_ocr
                    ),
                    processing_status="queued",
                    extraction_status="pending",
                )
            )

        except (
            InvalidPdfError,
            StorageUploadError,
        ) as exc:
            if storage_path:
                remove_file_from_storage(
                    supabase=supabase,
                    bucket=settings.storage_bucket,
                    storage_path=storage_path,
                )

            failed.append(
                DocumentUploadFailure(
                    original_filename=(
                        original_filename
                    ),
                    message=str(exc),
                )
            )

        except Exception as exc:
            if storage_path:
                remove_file_from_storage(
                    supabase=supabase,
                    bucket=settings.storage_bucket,
                    storage_path=storage_path,
                )

            failed.append(
                DocumentUploadFailure(
                    original_filename=(
                        original_filename
                    ),
                    message=(
                        "Dosya işlenirken beklenmeyen "
                        "bir hata oluştu."
                    ),
                )
            )

        finally:
            await file.close()

    if successful:
        supabase.table("projects").update(
            {
                "status": "documents_uploaded",
            }
        ).eq(
            "id",
            str(project_id),
        ).execute()

    return MultipleDocumentUploadResponse(
        successful=successful,
        failed=failed,
    )

@router.post(
    "/documents/{document_id}/process",
    status_code=status.HTTP_202_ACCEPTED,
)
async def queue_document_processing(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> dict[str, str]:
    supabase = get_supabase_admin()

    response = (
        supabase
        .table("project_documents")
        .select(
            "id, project_id, processing_status"
        )
        .eq("id", str(document_id))
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belge bulunamadı.",
        )

    document = response.data[0]

    get_accessible_project(
        supabase=supabase,
        project_id=document["project_id"],
        user_id=current_user.id,
    )

    if document["processing_status"] in {
        "queued",
        "processing",
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Belge zaten işleme sırasında.",
        )

    (
        supabase
        .table("project_documents")
        .update(
            {
                "processing_status": "queued",
                "extraction_status": "pending",
                "error_message": None,
            }
        )
        .eq("id", str(document_id))
        .execute()
    )

    background_tasks.add_task(
        process_document,
        document_id=str(document_id),
    )

    return {
        "document_id": str(document_id),
        "status": "queued",
    }


@router.get(
    "/documents/{document_id}",
)
async def get_document_detail(
    document_id: UUID,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> dict:
    supabase = get_supabase_admin()

    response = (
        supabase
        .table("project_documents")
        .select(
            (
                "id, project_id, original_filename, "
                "document_type, file_size_bytes, "
                "page_count, processing_status, "
                "extraction_status, "
                "extracted_character_count, "
                "extracted_word_count, chunk_count, "
                "error_message, created_at, updated_at"
            )
        )
        .eq("id", str(document_id))
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belge bulunamadı.",
        )

    document = response.data[0]

    get_accessible_project(
        supabase=supabase,
        project_id=document["project_id"],
        user_id=current_user.id,
    )

    return document