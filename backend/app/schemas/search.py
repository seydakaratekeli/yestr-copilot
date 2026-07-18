from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=1000,
    )

    limit: int = Field(
        default=8,
        ge=1,
        le=20,
    )

    minimum_similarity: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
    )


class SemanticSearchResult(BaseModel):
    id: str
    document_id: str
    project_id: str

    page_number: int
    chunk_index: int

    content: str

    document_type: str | None
    original_filename: str | None
    extraction_method: str | None

    similarity: float


class SemanticSearchResponse(BaseModel):
    query: str
    result_count: int
    results: list[SemanticSearchResult]