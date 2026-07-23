export type EvaluationStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed";

export type CriterionResultStatus =
  | "satisfied"
  | "not_satisfied"
  | "uncertain"
  | "not_applicable"
  | "manual_review"
  | "not_evaluated"
  | "failed";

export interface CriterionSet {
  id: string;
  code: string;
  name: string;
  version: string;
  description: string | null;
  status: string;
}

export interface EvaluationSummary {
  id: string;
  project_id: string;
  criterion_set_id: string;

  status: EvaluationStatus;

  total_score: number;
  maximum_score: number;
  score_percentage: number;

  satisfied_count: number;
  not_satisfied_count: number;
  uncertain_count: number;
  manual_review_count: number;

  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;

  created_at: string;
}

export interface CriterionResult {
  id: string;

  result_status: CriterionResultStatus;

  awarded_score: number;
  maximum_score: number;

  extracted_values: Record<
    string,
    unknown
  >;

  citations: Array<{
    source_id: string;
    document_id: string;
    original_filename: string;
    page_number: number;
    similarity: number;
    excerpt: string;
  }>;

  evidence_summary: string | null;

  missing_information: string[];
  warnings: string[];

  confidence: number;
  requires_manual_review: boolean;

  criteria: {
    code: string;
    title: string;
    category_code: string | null;
    category_name: string | null;
    display_order: number;
  };
}

export interface EvaluationDetail {
  evaluation: EvaluationSummary;
  results: CriterionResult[];
}