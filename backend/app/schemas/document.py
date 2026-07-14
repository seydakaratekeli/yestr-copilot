from typing import Literal

from pydantic import BaseModel


DocumentType = Literal[
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


class DocumentUploadResult(BaseModel):
    id: str
    original_filename: str
    document_type: str
    file_size_bytes: int
    page_count: int
    has_extractable_text: bool
    requires_ocr: bool
    processing_status: str
    extraction_status: str


class DocumentUploadFailure(BaseModel):
    original_filename: str
    message: str


class MultipleDocumentUploadResponse(BaseModel):
    successful: list[DocumentUploadResult]
    failed: list[DocumentUploadFailure]