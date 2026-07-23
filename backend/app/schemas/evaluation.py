from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


EvaluationStatus = Literal[
    "queued",
    "processing",
    "completed",
    "failed",
]


CriterionResultStatus = Literal[
    "satisfied",
    "not_satisfied",
    "uncertain",
    "not_applicable",
    "manual_review",
    "not_evaluated",
    "failed",
]


class StartEvaluationRequest(BaseModel):
    criterion_set_id: str


class EvaluationSummary(BaseModel):
    id: str
    project_id: str
    criterion_set_id: str

    status: EvaluationStatus

    total_score: float
    maximum_score: float
    score_percentage: float

    satisfied_count: int
    not_satisfied_count: int
    uncertain_count: int
    manual_review_count: int

    started_at: datetime | None
    completed_at: datetime | None

    error_message: str | None
    created_at: datetime


class CriterionEvaluationResult(BaseModel):
    id: str
    criterion_id: str

    criterion_code: str
    criterion_title: str
    category_name: str | None

    result_status: CriterionResultStatus

    awarded_score: float
    maximum_score: float

    extracted_values: dict[str, Any]
    citations: list[dict[str, Any]]

    evidence_summary: str | None

    missing_information: list[str]
    warnings: list[str]

    confidence: float
    requires_manual_review: bool


class EvaluationDetail(BaseModel):
    evaluation: EvaluationSummary
    results: list[CriterionEvaluationResult]