import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisTargetCreate(BaseModel):
    """Owner is never accepted from the client; it is derived from the session."""

    name: str = Field(min_length=1, max_length=200)
    source_url: str = Field(min_length=1)


class AnalysisTargetRename(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class AnalysisTargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    platform: str
    source_url: str
    created_at: datetime
    updated_at: datetime


class AnalysisTargetListResponse(BaseModel):
    items: list[AnalysisTargetResponse]
