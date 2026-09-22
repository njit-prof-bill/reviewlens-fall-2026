"""Read models over persisted reviews and ingestion runs.

Ownership is inherited through the analysis target, so every entry point either
takes a target already verified by `analysis_target_service.get_owned_target`
or joins to the target and filters on the owner (S1-BR-009).
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import AnalysisTarget, IngestionRun, Review
from app.errors import ResourceNotFoundError


def list_reviews(
    session: Session,
    target_id: uuid.UUID,
    limit: int,
    offset: int,
    min_rating: float | None = None,
    max_rating: float | None = None,
    reviewed_after: datetime | None = None,
    reviewed_before: datetime | None = None,
) -> tuple[list[Review], int]:
    filters = [Review.analysis_target_id == target_id, Review.is_current.is_(True)]
    if min_rating is not None:
        filters.append(Review.rating >= min_rating)
    if max_rating is not None:
        filters.append(Review.rating <= max_rating)
    if reviewed_after is not None:
        filters.append(Review.reviewed_at >= reviewed_after)
    if reviewed_before is not None:
        filters.append(Review.reviewed_at <= reviewed_before)

    total = session.scalar(select(func.count()).select_from(Review).where(*filters))
    statement = (
        select(Review)
        .where(*filters)
        .order_by(Review.reviewed_at.desc().nullslast(), Review.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement)), int(total or 0)


def list_runs(session: Session, target_id: uuid.UUID) -> list[IngestionRun]:
    statement = (
        select(IngestionRun)
        .where(IngestionRun.analysis_target_id == target_id)
        .order_by(IngestionRun.created_at.desc())
    )
    return list(session.scalars(statement))


def get_latest_run(session: Session, target_id: uuid.UUID) -> IngestionRun | None:
    statement = (
        select(IngestionRun)
        .where(IngestionRun.analysis_target_id == target_id)
        .order_by(IngestionRun.created_at.desc())
        .limit(1)
    )
    return session.scalars(statement).one_or_none()


def get_owned_run(
    session: Session, owner_user_id: uuid.UUID, run_id: uuid.UUID
) -> IngestionRun:
    statement = (
        select(IngestionRun)
        .join(AnalysisTarget, IngestionRun.analysis_target_id == AnalysisTarget.id)
        .where(
            IngestionRun.id == run_id,
            AnalysisTarget.owner_user_id == owner_user_id,
        )
    )
    run = session.scalars(statement).one_or_none()
    if run is None:
        raise ResourceNotFoundError("Ingestion run not found")
    return run


def build_summary(session: Session, target: AnalysisTarget) -> dict:
    """Aggregate persisted review data. No values are model-generated."""
    aggregates = session.execute(
        select(
            func.count(Review.id),
            func.avg(Review.rating),
            func.min(Review.reviewed_at),
            func.max(Review.reviewed_at),
        ).where(Review.analysis_target_id == target.id, Review.is_current.is_(True))
    ).one()

    count, average, earliest, latest = aggregates
    return {
        "entity_name": target.name,
        "platform": target.platform,
        "source_url": target.source_url,
        "reviews_collected": int(count or 0),
        "average_rating": round(float(average), 2) if average is not None else None,
        "earliest_review": earliest,
        "latest_review": latest,
        "latest_run": get_latest_run(session, target.id),
    }
