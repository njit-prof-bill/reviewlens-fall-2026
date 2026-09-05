import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.ingestion import IngestionRunResponse


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    review_text: str
    rating: float
    reviewer_name: str | None = None
    reviewed_at: datetime | None = None
    source_review_id: str | None = None
    review_url: str | None = None


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    limit: int
    offset: int


class AnalysisTargetSummaryResponse(BaseModel):
    """Aggregates computed from persisted reviews. Never model-generated."""

    entity_name: str
    platform: str
    source_url: str
    reviews_collected: int
    average_rating: float | None = None
    earliest_review: datetime | None = None
    latest_review: datetime | None = None
    latest_run: IngestionRunResponse | None = None
