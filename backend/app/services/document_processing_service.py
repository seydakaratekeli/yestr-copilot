from datetime import datetime, timezone

from supabase import Client

from app.core.config import settings
from app.services.chunk_service import (
    split_text_into_chunks,
)
from app.services.pdf_extraction_service import (
    extract_pdf_pages,
)
from app.services.storage_service import (
    download_file_from_storage,
)


def process_document(
    *,
    document_id: str,
) -> None:
    from app.core.supabase import get_supabase_admin

    supabase = get_supabase_admin()

    try:
        document = _get_document(
            supabase=supabase,
            document_id=document_id,
        )

        _mark_processing(
            supabase=supabase,
            document_id=document_id,
        )

        pdf_content = download_file_from_storage(
            supabase=supabase,
            bucket=settings.storage_bucket,
            storage_path=document["storage_path"],
        )

        extracted_pages = extract_pdf_pages(
            pdf_content
        )

        _delete_previous_extraction(
            supabase=supabase,
            document_id=document_id,
        )

        total_character_count = 0
        total_word_count = 0
        total_chunk_count = 0
        failed_page_count = 0
        ocr_page_count = 0

        for page in extracted_pages:
            page_record = _insert_page(
                supabase=supabase,
                document=document,
                page=page,
            )

            if page.requires_ocr:
                failed_page_count += 1
            elif page.extraction_method == "ocr":
                ocr_page_count += 1

            total_character_count += (
                page.character_count
            )

            total_word_count += page.word_count

            chunks = split_text_into_chunks(
                page.cleaned_text,
                chunk_size=(
                    settings.chunk_size_characters
                ),
                overlap=(
                    settings
                    .chunk_overlap_characters
                ),
                minimum_chunk_size=(
                    settings
                    .minimum_chunk_characters
                ),
            )

            if chunks:
                chunk_records = []

                for chunk in chunks:
                    chunk_records.append(
                        {
                            "document_id": (
                                document_id
                            ),
                            "project_id": (
                                document[
                                    "project_id"
                                ]
                            ),
                            "page_id": (
                                page_record["id"]
                            ),
                            "page_number": (
                                page.page_number
                            ),
                            "chunk_index": (
                                chunk.index
                            ),
                            "content": (
                                chunk.content
                            ),
                            "character_count": (
                                chunk
                                .character_count
                            ),
                            "word_count": (
                                chunk.word_count
                            ),
                            "section_title": None,
                            "block_type": "text",
                            "metadata": {
                                "document_type": (
                                    document["document_type"]
                                ),
                                "original_filename": (
                                    document["original_filename"]
                                ),
                                "page_number": (
                                    page.page_number
                                ),
                                "extraction_method": (
                                    page.extraction_method
                                ),
                                "ocr_language": (
                                    settings.ocr_languages
                                    if page.extraction_method == "ocr"
                                    else None
                                ),
                                "ocr_dpi": (
                                    settings.ocr_dpi
                                    if page.extraction_method == "ocr"
                                    else None
                                ),
                            },
                            "embedding_status": (
                                "pending"
                            ),
                        }
                    )

                (
                    supabase
                    .table("document_chunks")
                    .insert(chunk_records)
                    .execute()
                )

                total_chunk_count += len(chunks)

        if failed_page_count == 0:
            final_extraction_status = "completed"
        elif failed_page_count < len(extracted_pages):
            final_extraction_status = "partial"
        else:
            final_extraction_status = "failed"

        (
            supabase
            .table("project_documents")
            .update(
                {
                    "processing_status": (
                        "completed"
                    ),
                    "extraction_status": (
                        final_extraction_status
                    ),
                    "extracted_character_count": (
                        total_character_count
                    ),
                    "extracted_word_count": (
                        total_word_count
                    ),
                    "chunk_count": (
                        total_chunk_count
                    ),
                    "processing_completed_at": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                    "native_page_count": (
                        len(extracted_pages)
                        - ocr_page_count
                        - failed_page_count
                    ),
                    "ocr_page_count": ocr_page_count,
                    "failed_page_count": failed_page_count,
                    "error_message": None,
                }
            )
            .eq("id", document_id)
            .execute()
        )

    except Exception as exc:
        (
            supabase
            .table("project_documents")
            .update(
                {
                    "processing_status": (
                        "failed"
                    ),
                    "extraction_status": (
                        "failed"
                    ),
                    "error_message": str(exc)[
                        :1000
                    ],
                    "processing_completed_at": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                }
            )
            .eq("id", document_id)
            .execute()
        )

        # Background task içindeki hata terminalde
        # görülebilsin.
        print(
            f"Document processing failed "
            f"for {document_id}: {exc}"
        )


def _get_document(
    *,
    supabase: Client,
    document_id: str,
) -> dict:
    response = (
        supabase
        .table("project_documents")
        .select(
            (
                "id, project_id, storage_path, "
                "document_type, original_filename"
            )
        )
        .eq("id", document_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise ValueError(
            "İşlenecek belge bulunamadı."
        )

    return response.data[0]


def _mark_processing(
    *,
    supabase: Client,
    document_id: str,
) -> None:
    (
        supabase
        .table("project_documents")
        .update(
            {
                "processing_status": (
                    "processing"
                ),
                "extraction_status": (
                    "processing"
                ),
                "processing_started_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
                "processing_completed_at": None,
                "error_message": None,
            }
        )
        .eq("id", document_id)
        .execute()
    )


def _delete_previous_extraction(
    *,
    supabase: Client,
    document_id: str,
) -> None:
    # Sayfalar silindiğinde page_id ilişkili
    # chunk kayıtları cascade ile silinir.
    (
        supabase
        .table("document_pages")
        .delete()
        .eq("document_id", document_id)
        .execute()
    )

def _insert_page(
    *,
    supabase: Client,
    document: dict,
    page,
) -> dict:
    processing_status = (
        "completed"
        if not page.requires_ocr
        else "failed"
    )

    response = (
        supabase
        .table("document_pages")
        .insert(
            {
                "document_id": document["id"],
                "project_id": (
                    document["project_id"]
                ),
                "page_number": (
                    page.page_number
                ),
                "raw_text": page.raw_text,
                "cleaned_text": (
                    page.cleaned_text
                ),
                "character_count": (
                    page.character_count
                ),
                "word_count": (
                    page.word_count
                ),
                "extraction_method": (
                    page.extraction_method
                ),
                "extraction_confidence": (
                    page.extraction_confidence
                ),
                "requires_ocr": (
                    page.requires_ocr
                ),
                "ocr_attempted": (
                    page.ocr_attempted
                ),
                "ocr_error": (
                    page.ocr_error
                ),
                "ocr_language": (
                    settings.ocr_languages
                    if page.ocr_attempted
                    else None
                ),
                "ocr_dpi": (
                    settings.ocr_dpi
                    if page.ocr_attempted
                    else None
                ),
                "processing_status": (
                    processing_status
                ),
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "PDF sayfası veritabanına "
            "kaydedilemedi."
        )

    return response.data[0]