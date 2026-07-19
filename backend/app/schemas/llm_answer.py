from typing import Literal

from pydantic import BaseModel, Field


class LlmGroundedAnswer(BaseModel):
    status: Literal[
        "answered",
        "insufficient_evidence",
        "conflicting_evidence",
    ]

    answer: str = Field(
        min_length=1,
        max_length=4000,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    citation_ids: list[str]

    missing_information: list[str]

    warnings: list[str]