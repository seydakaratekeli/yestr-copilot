from typing import Literal

from pydantic import BaseModel, Field


AnswerStatus = Literal[
    "answered",
    "insufficient_evidence",
    "conflicting_evidence",
]


class ProjectQuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )

    search_limit: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    minimum_similarity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class AnswerCitation(BaseModel):
    source_id: str
    document_id: str
    original_filename: str
    page_number: int
    document_type: str | None
    similarity: float
    excerpt: str


class ProjectQuestionResponse(BaseModel):
    question: str

    status: AnswerStatus
    answer: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    citations: list[AnswerCitation]

    missing_information: list[str]
    warnings: list[str]

    retrieved_source_count: int