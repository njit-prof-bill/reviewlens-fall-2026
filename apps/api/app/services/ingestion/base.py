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


@dataclass(slots=True)
class IngestionResult:
    reviews: list[RawReview]
    entity_name: str | None = None


class IngestionError(Exception):
    """Aborts a whole run. Carries a stable code and a user-safe message."""

    def __init__(self, code: IngestionErrorCode, technical_detail: str | None = None):
        self.code = code
        self.message = INGESTION_ERROR_MESSAGES[code]
        self.technical_detail = technical_detail
        super().__init__(technical_detail or self.message)


class ReviewSource(Protocol):
    def fetch(self, target: AnalysisTarget) -> IngestionResult: ...


class FallbackReviewSource:
    """Try ordered providers only when the preceding provider is unavailable."""

    _RETRYABLE = frozenset(
        {
            IngestionErrorCode.PROVIDER_TIMEOUT,
            IngestionErrorCode.PROVIDER_UNAVAILABLE,
            IngestionErrorCode.PROVIDER_QUOTA_EXCEEDED,
        }
    )

    def __init__(self, sources: list[ReviewSource]):
        if not sources:
            raise ValueError("At least one review source is required")
        self._sources = sources

    def fetch(self, target: AnalysisTarget) -> IngestionResult:
        last_error: IngestionError | None = None
        for index, source in enumerate(self._sources):
            try:
                return source.fetch(target)
            except IngestionError as exc:
                if exc.code not in self._RETRYABLE or index == len(self._sources) - 1:
                    raise
                last_error = exc

        if last_error:
            raise last_error
        raise IngestionError(IngestionErrorCode.PROVIDER_NOT_CONFIGURED)
