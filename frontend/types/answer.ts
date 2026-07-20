export type AnswerStatus =
  | "answered"
  | "insufficient_evidence"
  | "conflicting_evidence";

export interface AnswerCitation {
  source_id: string;
  document_id: string;
  original_filename: string;
  page_number: number;
  document_type: string | null;
  similarity: number;
  excerpt: string;
}

export interface ProjectQuestionResponse {
  question: string;

  status: AnswerStatus;
  answer: string;
  confidence: number;

  citations: AnswerCitation[];

  missing_information: string[];
  warnings: string[];

  retrieved_source_count: number;
}