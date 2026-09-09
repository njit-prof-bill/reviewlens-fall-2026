"""Drives one ingestion attempt and records its result state (S1-023).

A failed run persists zero reviews. Technical detail is logged server-side; the
run stores only a user-safe message (S1-BR-024).
"""

import logging
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
from app.services.ingestion.normalizer import normalize_all

logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]


def review_dedupe_key(
    review_text: str,
    rating: float,
    reviewer_name: str | None,
    reviewed_at: datetime | None,
    source_review_id: str | None,
) -> str:
    """Return a stable source ID or fallback content fingerprint."""
    if source_review_id:
        return sha256(f"source:{source_review_id}".encode()).hexdigest()
    normalized = "\x1f".join(
        (
            review_text.strip().casefold(),
            str(rating),
            (reviewer_name or "").strip().casefold(),
            reviewed_at.isoformat() if reviewed_at else "",
        )
    )
    return sha256(normalized.encode()).hexdigest()


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
    duplicates: int = 0,
    rejection_reasons: dict[str, int] | None = None,
    error_code: IngestionErrorCode | None = None,
) -> None:
    run.status = status.value
    run.reviews_ingested = ingested
    run.reviews_rejected = rejected
    run.reviews_duplicate = duplicates
    run.rejection_reasons = rejection_reasons or None
    run.error_code = error_code.value if error_code else None
    run.error_message = INGESTION_ERROR_MESSAGES[error_code] if error_code else None
    run.completed_at = datetime.now(UTC)
    session.add(run)
    session.commit()


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

        existing = list(
            session.scalars(
                select(Review).where(Review.analysis_target_id == target.id)
            )
        )
        existing_keys = {
            review.dedupe_key
            or review_dedupe_key(
                review.review_text,
                review.rating,
                review.reviewer_name,
                review.reviewed_at,
                review.source_review_id,
            )
            for review in existing
        }
        new_reviews: list[Review] = []
        duplicates = 0
        for item in accepted:
            dedupe_key = review_dedupe_key(
                item.review_text,
                item.rating,
                item.reviewer_name,
                item.reviewed_at,
                item.source_review_id,
            )
            if dedupe_key in existing_keys:
                duplicates += 1
                continue
            existing_keys.add(dedupe_key)
            new_reviews.append(
                Review(
                    analysis_target_id=target.id,
                    ingestion_run_id=run.id,
                    review_text=item.review_text,
                    rating=item.rating,
                    reviewer_name=item.reviewer_name,
                    reviewed_at=item.reviewed_at,
                    source_review_id=item.source_review_id,
                    dedupe_key=dedupe_key,
                    review_url=item.review_url,
                    source_metadata=item.source_metadata,
                )
            )
        session.add_all(new_reviews)
        session.commit()

        status = IngestionStatus.PARTIAL if rejected else IngestionStatus.SUCCEEDED
        _finish(
            session,
            run,
            status,
            ingested=len(new_reviews),
            rejected=len(rejected),
            duplicates=duplicates,
            rejection_reasons=dict(Counter(item.reason for item in rejected)),
        )
    finally:
        session.close()
