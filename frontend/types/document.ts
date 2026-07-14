export type DocumentType =
  | "site_plan"
  | "floor_plan"
  | "section"
  | "facade"
  | "energy_report"
  | "technical_specification"
  | "product_datasheet"
  | "mechanical_report"
  | "electrical_report"
  | "other";

export interface ProjectDocument {
  id: string;
  project_id: string;
  uploaded_by: string;

  original_filename: string;
  storage_path: string;

  document_type: DocumentType;
  mime_type: string;

  file_size_bytes: number;
  page_count: number | null;

  processing_status:
    | "uploaded"
    | "queued"
    | "processing"
    | "completed"
    | "failed";

  extraction_status:
    | "pending"
    | "processing"
    | "completed"
    | "failed";

  error_message: string | null;

  created_at: string;
  updated_at: string;
}

export interface UploadedDocumentResult {
  id: string;
  original_filename: string;
  document_type: DocumentType;
  file_size_bytes: number;
  page_count: number;
  has_extractable_text: boolean;
  requires_ocr: boolean;
  processing_status: string;
  extraction_status: string;
}

export interface FailedDocumentResult {
  original_filename: string;
  message: string;
}

export interface MultipleDocumentUploadResponse {
  successful: UploadedDocumentResult[];
  failed: FailedDocumentResult[];
}