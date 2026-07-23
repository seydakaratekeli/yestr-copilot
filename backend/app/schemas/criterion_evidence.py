from typing import Any, Literal

from pydantic import BaseModel, Field


class CriterionEvidenceExtraction(BaseModel):
    evidence_status: Literal[
        "found",
        "not_found",
        "conflicting",
        "ambiguous",
    ]

    extracted_values: dict[str, Any]

    evidence_summary: str

    citation_ids: list[str]

    missing_information: list[str]

    warnings: list[str]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )