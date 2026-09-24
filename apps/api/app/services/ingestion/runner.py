"""Drives one ingestion attempt and records its result state (S1-023).

A failed run persists zero reviews. Technical detail is logged server-side; the
run stores only a user-safe message (S1-BR-024).
"""

import logging
import re
import uuid
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import IngestionRun, Review
from app.db.session import SessionLocal
from app.domain import (
    INGESTION_ERROR_MESSAGES,
    IngestionErrorCode,
    IngestionSourceKind,
    IngestionStatus,
)
from app.services.ingestion.base import IngestionError, ReviewSource
from app.services.ingestion.normalizer import NormalizedReview, normalize_all

logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]
_WHITESPACE = re.compile(r"\s+")


def start_ingestion_run(
    session: Session, target_id: uuid.UUID, source_kind: IngestionSourceKind
) -> IngestionRun:
    """Record a pending run so the caller can poll it while work happens."""
    run = IngestionRun(
        analysis_target_id=target_id,
        status=IngestionStatus.PENDING.value,
        source_kind=source_kind.value,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def _finish(
    session: Session,
    run: IngestionRun,
    status: IngestionStatus,
    ingested: int = 0,
    rejected: int = 0,
    rejection_reasons: dict[str, int] | None = None,
    error_code: IngestionErrorCode | None = None,
) -> None:
    run.status = status.value
    run.reviews_ingested = ingested
    run.reviews_rejected = rejected
    run.rejection_reasons = rejection_reasons or None
    run.error_code = error_code.value if error_code else None
    run.error_message = INGESTION_ERROR_MESSAGES[error_code] if error_code else None
    run.completed_at = datetime.now(UTC)
    session.add(run)
    session.commit()


def _identity_key(item: NormalizedReview) -> str:
    if item.source_review_id:
        return f"source:{item.source_review_id.strip().lower()}"

    reviewed_at = item.reviewed_at.date().isoformat() if item.reviewed_at else ""
    reviewer_name = (item.reviewer_name or "").strip().lower()
    review_url = (item.review_url or "").strip().lower()
    text = _WHITESPACE.sub(" ", item.review_text.strip().lower())
    fingerprint = sha256(
        "|".join(
            [
                f"{item.rating:.2f}",
                reviewer_name,
                reviewed_at,
                review_url,
                text,
            ]
        ).encode("utf-8")
    ).hexdigest()
    return f"fingerprint:{fingerprint}"


def _promote_reviews(
    session: Session, run: IngestionRun, accepted: list[NormalizedReview]
) -> int:
    incoming = {_identity_key(item): item for item in accepted}
    if not incoming:
        return 0

    existing = {
        review.review_identity_key: review
        for review in session.scalars(
            select(Review).where(
                Review.analysis_target_id == run.analysis_target_id,
                Review.review_identity_key.in_(incoming.keys()),
            )
        )
    }

    for identity_key, item in incoming.items():
        review = existing.get(identity_key)
        if review is None:
            review = Review(
                analysis_target_id=run.analysis_target_id,
                review_identity_key=identity_key,
            )

        review.ingestion_run_id = run.id
        review.is_current = True
        review.review_text = item.review_text
        review.rating = item.rating
        review.reviewer_name = item.reviewer_name
        review.reviewed_at = item.reviewed_at
        review.source_review_id = item.source_review_id
        review.review_url = item.review_url
        review.source_metadata = item.source_metadata
        session.add(review)

    return len(incoming)


def execute_ingestion_run(
    run_id: uuid.UUID,
    source: ReviewSource,
    session_factory: SessionFactory | None = None,
) -> None:
    """Run to completion, always leaving the run in a terminal state."""
    session = (session_factory or SessionLocal)()
    try:
        run = session.get(IngestionRun, run_id)
        if run is None:
            logger.error("Ingestion run %s disappeared before execution", run_id)
            return

        target = run.analysis_target
        run.status = IngestionStatus.PROCESSING.value
        run.started_at = datetime.now(UTC)
        session.add(run)
        session.commit()

        try:
            result = source.fetch(target)
            accepted, rejected = normalize_all(result.reviews)
        except IngestionError as exc:
            logger.warning(
                "Ingestion run %s failed (%s): %s",
                run_id,
                exc.code.value,
                exc.technical_detail,
            )
            _finish(session, run, IngestionStatus.FAILED, error_code=exc.code)
            return
        except Exception:
            logger.exception("Ingestion run %s failed unexpectedly", run_id)
            _finish(
                session,
                run,
                IngestionStatus.FAILED,
                error_code=IngestionErrorCode.UNEXPECTED_ERROR,
            )
            return

        if not accepted:
            _finish(
                session,
                run,
                IngestionStatus.FAILED,
                rejected=len(rejected),
                rejection_reasons=dict(Counter(item.reason for item in rejected)),
                error_code=IngestionErrorCode.NO_USABLE_REVIEWS,
            )
            return

        if result.entity_name and target.name == "Untitled Analysis":
            target.name = result.entity_name[:200]
            session.add(target)

        ingested = _promote_reviews(session, run, accepted)
        session.commit()

        status = IngestionStatus.PARTIAL if rejected else IngestionStatus.SUCCEEDED
        _finish(
            session,
            run,
            status,
            ingested=ingested,
            rejected=len(rejected),
            rejection_reasons=dict(Counter(item.reason for item in rejected)),
        )
    finally:
        session.close()
