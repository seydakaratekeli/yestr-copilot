from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.answer import AnswerCitation


class ConversationCreateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=200,
    )


class ConversationSummary(BaseModel):
    id: str
    project_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationMessage(BaseModel):
    id: str
    conversation_id: str
    project_id: str

    role: Literal["user", "assistant"]
    content: str

    answer_status: str | None
    confidence: float | None

    citations: list[AnswerCitation]
    missing_information: list[str]
    warnings: list[str]

    retrieved_source_count: int
    error_message: str | None

    created_at: datetime


class ConversationDetail(BaseModel):
    conversation: ConversationSummary
    messages: list[ConversationMessage]


class ConversationQuestionRequest(BaseModel):
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
        ge=0,
        le=1,
    )


class ConversationQuestionResponse(BaseModel):
    conversation_id: str
    user_message: ConversationMessage
    assistant_message: ConversationMessage