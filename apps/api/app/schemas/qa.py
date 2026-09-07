import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain import QAResultKind


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question must contain text")
        return value


class QAEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: uuid.UUID | None = None
    excerpt: str
    rating: float | None = None
    reviewer_name: str | None = None
    reviewed_at: datetime | None = None


class QAEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    analysis_target_id: uuid.UUID
    question: str
    answer: str
    result_kind: QAResultKind
    provider: str
    model: str
    context_review_count: int
    created_at: datetime
    evidence: list[QAEvidenceResponse]


class QAEntryListResponse(BaseModel):
    items: list[QAEntryResponse]
