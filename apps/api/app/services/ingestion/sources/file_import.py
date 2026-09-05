"""Recovery path when the live review source is unavailable (S1-BR-027).

Subordinate to URL-driven collection; never the primary ingestion gesture.
"""

import csv
import io
import json
from typing import Any

from app.db.models import AnalysisTarget
from app.domain import IngestionErrorCode
from app.services.ingestion.base import IngestionError, IngestionResult, RawReview

_TEXT_KEYS = ("review_text", "text", "snippet", "review", "comment", "body")
_RATING_KEYS = ("rating", "stars", "score", "star_rating")
_REVIEWER_KEYS = ("reviewer_name", "reviewer", "author", "user", "name")
_DATE_KEYS = ("reviewed_at", "iso_date", "date", "published_at", "time")
_ID_KEYS = ("source_review_id", "review_id", "id")
_URL_KEYS = ("review_url", "url", "link")

_KNOWN_KEYS = frozenset(
    _TEXT_KEYS + _RATING_KEYS + _REVIEWER_KEYS + _DATE_KEYS + _ID_KEYS + _URL_KEYS
)


def _pick(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return None


def _to_raw_review(record: dict[str, Any]) -> RawReview:
    normalized = {
        str(key).strip().lower().replace(" ", "_"): value
        for key, value in record.items()
        if key is not None
    }
    extras = {
        key: value
        for key, value in normalized.items()
        if key not in _KNOWN_KEYS and value not in (None, "")
    }
    return RawReview(
        review_text=_pick(normalized, _TEXT_KEYS),
        rating=_pick(normalized, _RATING_KEYS),
        reviewer_name=_pick(normalized, _REVIEWER_KEYS),
        reviewed_at=_pick(normalized, _DATE_KEYS),
        source_review_id=_pick(normalized, _ID_KEYS),
        review_url=_pick(normalized, _URL_KEYS),
        source_metadata=extras,
    )


def _decode(payload: bytes) -> str:
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise IngestionError(IngestionErrorCode.SOURCE_UNPARSEABLE, str(exc)) from exc


def parse_csv(payload: bytes) -> list[RawReview]:
    reader = csv.DictReader(io.StringIO(_decode(payload)))
    if not reader.fieldnames:
        raise IngestionError(
            IngestionErrorCode.SOURCE_UNPARSEABLE, "CSV has no header row"
        )

    try:
        rows = list(reader)
    except csv.Error as exc:
        raise IngestionError(IngestionErrorCode.SOURCE_UNPARSEABLE, str(exc)) from exc

    if not rows:
        raise IngestionError(
            IngestionErrorCode.SOURCE_UNPARSEABLE, "CSV contains no data rows"
        )

    return [_to_raw_review(row) for row in rows]


def parse_json(payload: bytes) -> list[RawReview]:
    try:
        document = json.loads(_decode(payload))
    except json.JSONDecodeError as exc:
        raise IngestionError(IngestionErrorCode.SOURCE_UNPARSEABLE, str(exc)) from exc

    if isinstance(document, dict):
        document = document.get("reviews")

    if not isinstance(document, list):
        raise IngestionError(
            IngestionErrorCode.SOURCE_UNPARSEABLE,
            "Expected a JSON array of reviews or an object with a 'reviews' array",
        )

    records = [entry for entry in document if isinstance(entry, dict)]
    if not records:
        raise IngestionError(
            IngestionErrorCode.SOURCE_UNPARSEABLE, "No review objects found"
        )

    return [_to_raw_review(record) for record in records]


def parse_upload(filename: str | None, payload: bytes) -> list[RawReview]:
    if not payload.strip():
        raise IngestionError(IngestionErrorCode.SOURCE_UNPARSEABLE, "Empty file")

    if (filename or "").lower().endswith(".json"):
        return parse_json(payload)
    return parse_csv(payload)


class FileImportSource:
    def __init__(self, filename: str | None, payload: bytes):
        self._filename = filename
        self._payload = payload

    def fetch(self, target: AnalysisTarget) -> IngestionResult:
        return IngestionResult(reviews=parse_upload(self._filename, self._payload))
