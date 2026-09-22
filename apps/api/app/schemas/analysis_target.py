import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalysisTargetNameMixin(BaseModel):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def name_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must contain text")
        return value


class AnalysisTargetCreate(AnalysisTargetNameMixin):
    """Owner is never accepted from the client; it is derived from the session."""

    source_url: str = Field(min_length=1)


class AnalysisTargetRename(AnalysisTargetNameMixin):
    pass


class AnalysisTargetCopy(AnalysisTargetNameMixin):
    pass


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
