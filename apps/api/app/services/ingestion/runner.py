"""Drives one ingestion attempt and records its result state (S1-023).

A failed run persists zero reviews. Technical detail is logged server-side; the
run stores only a user-safe message (S1-BR-024).
"""

import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime

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
    error_code: IngestionErrorCode | None = None,
) -> None:
    run.status = status.value
    run.reviews_ingested = ingested
    run.reviews_rejected = rejected
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
            raw_reviews = source.fetch(target)
            accepted, rejected = normalize_all(raw_reviews)
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
                error_code=IngestionErrorCode.NO_USABLE_REVIEWS,
            )
            return

        session.add_all(
            Review(
                analysis_target_id=target.id,
                ingestion_run_id=run.id,
                review_text=item.review_text,
                rating=item.rating,
                reviewer_name=item.reviewer_name,
                reviewed_at=item.reviewed_at,
                source_review_id=item.source_review_id,
                review_url=item.review_url,
                source_metadata=item.source_metadata,
            )
            for item in accepted
        )
        session.commit()

        status = IngestionStatus.PARTIAL if rejected else IngestionStatus.SUCCEEDED
        _finish(
            session,
            run,
            status,
            ingested=len(accepted),
            rejected=len(rejected),
        )
    finally:
        session.close()
