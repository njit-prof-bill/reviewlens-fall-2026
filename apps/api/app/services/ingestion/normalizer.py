"""Turns source-shaped records into the canonical Review representation.

Shared by every source so the persisted shape is provider-independent (S1-021).
A malformed individual record is rejected without aborting the batch, and no
missing field is ever invented (S1-BR-024).
"""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.services.ingestion.base import RawReview

_LEADING_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")
_MIN_RATING = 1.0
_MAX_RATING = 5.0


@dataclass(slots=True)
class NormalizedReview:
    review_text: str
    rating: float
    reviewer_name: str | None = None
    reviewed_at: datetime | None = None
    source_review_id: str | None = None
    review_url: str | None = None
    source_metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class RejectedRecord:
    reason: str


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_rating(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        rating = float(value)
    else:
        text = _clean_text(value)
        if text is None:
            return None
        match = _LEADING_NUMBER.search(text)
        if match is None:
            return None
        try:
            rating = float(match.group().replace(",", "."))
        except ValueError:
            return None

    if not _MIN_RATING <= rating <= _MAX_RATING:
        return None
    return rating


def _coerce_datetime(value: Any) -> datetime | None:
    """Optional metadata: unparseable values become None rather than a rejection."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=UTC)
        except (OverflowError, OSError, ValueError):
            return None

    text = _clean_text(value)
    if text is None:
        return None

    candidate = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def normalize(raw: RawReview) -> NormalizedReview | RejectedRecord:
    review_text = _clean_text(raw.review_text)
    if review_text is None:
        return RejectedRecord(reason="missing_review_text")

    rating = _coerce_rating(raw.rating)
    if rating is None:
        return RejectedRecord(reason="missing_or_invalid_rating")

    return NormalizedReview(
        review_text=review_text,
        rating=rating,
        reviewer_name=_clean_text(raw.reviewer_name),
        reviewed_at=_coerce_datetime(raw.reviewed_at),
        source_review_id=_clean_text(raw.source_review_id),
        review_url=_clean_text(raw.review_url),
        source_metadata=raw.source_metadata or None,
    )


def normalize_all(
    raws: list[RawReview],
) -> tuple[list[NormalizedReview], list[RejectedRecord]]:
    accepted: list[NormalizedReview] = []
    rejected: list[RejectedRecord] = []

    for raw in raws:
        result = normalize(raw)
        if isinstance(result, NormalizedReview):
            accepted.append(result)
        else:
            rejected.append(result)

    return accepted, rejected
