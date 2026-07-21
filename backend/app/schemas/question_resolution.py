from pydantic import BaseModel, Field


class ResolvedConversationQuestion(BaseModel):
    is_follow_up: bool

    resolved_query: str = Field(
        min_length=3,
        max_length=1500,
    )

    referenced_message_ids: list[str]

    resolution_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )