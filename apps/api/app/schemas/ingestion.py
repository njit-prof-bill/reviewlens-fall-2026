import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain import IngestionSourceKind


class StartIngestionRequest(BaseModel):
    source_kind: IngestionSourceKind = IngestionSourceKind.URL_FETCH


class IngestionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    analysis_target_id: uuid.UUID
    status: str
    source_kind: str
    reviews_ingested: int
    reviews_rejected: int
    reviews_duplicate: int
    rejection_reasons: dict[str, int] | None = None
    error_code: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class IngestionRunListResponse(BaseModel):
    items: list[IngestionRunResponse]
