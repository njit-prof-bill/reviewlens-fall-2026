"""The contract every review source implements."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.db.models import AnalysisTarget
from app.domain import INGESTION_ERROR_MESSAGES, IngestionErrorCode


@dataclass(slots=True)
class RawReview:
    """A single record as the source presented it, before normalization."""

    review_text: Any = None
    rating: Any = None
    reviewer_name: Any = None
    reviewed_at: Any = None
    source_review_id: Any = None
    review_url: Any = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


class IngestionError(Exception):
    """Aborts a whole run. Carries a stable code and a user-safe message."""

    def __init__(self, code: IngestionErrorCode, technical_detail: str | None = None):
        self.code = code
        self.message = INGESTION_ERROR_MESSAGES[code]
        self.technical_detail = technical_detail
        super().__init__(technical_detail or self.message)


class ReviewSource(Protocol):
    def fetch(self, target: AnalysisTarget) -> list[RawReview]: ...
