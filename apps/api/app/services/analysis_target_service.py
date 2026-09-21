"""Analysis target persistence.

Every function takes the authenticated owner id first and scopes its query by it.
`get_owned_target` is the chokepoint every child-resource route must call before
touching reviews or ingestion runs (S1-BR-009).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalysisTarget, IngestionRun, Review
from app.domain import IngestionSourceKind, IngestionStatus
from app.errors import ResourceNotFoundError
from app.services.source_url import detect_platform, validate_source_url


def create_target(
    session: Session, owner_user_id: uuid.UUID, name: str, source_url: str
) -> AnalysisTarget:
    normalized_url = validate_source_url(source_url)
    platform = detect_platform(normalized_url)

    target = AnalysisTarget(
        owner_user_id=owner_user_id,
        name=name.strip(),
        platform=platform.value,
        source_url=normalized_url,
    )
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def list_targets(session: Session, owner_user_id: uuid.UUID) -> list[AnalysisTarget]:
    statement = (
        select(AnalysisTarget)
        .where(AnalysisTarget.owner_user_id == owner_user_id)
        .order_by(AnalysisTarget.created_at.desc())
    )
    return list(session.scalars(statement))


def get_owned_target(
    session: Session, owner_user_id: uuid.UUID, target_id: uuid.UUID
) -> AnalysisTarget:
    statement = select(AnalysisTarget).where(
        AnalysisTarget.id == target_id,
        AnalysisTarget.owner_user_id == owner_user_id,
    )
    target = session.scalars(statement).one_or_none()
    if target is None:
        raise ResourceNotFoundError("Analysis target not found")
    return target


def rename_target(
    session: Session, owner_user_id: uuid.UUID, target_id: uuid.UUID, name: str
) -> AnalysisTarget:
    target = get_owned_target(session, owner_user_id, target_id)
    target.name = name.strip()
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def copy_target(
    session: Session, owner_user_id: uuid.UUID, target_id: uuid.UUID, name: str
) -> AnalysisTarget:
    source = get_owned_target(session, owner_user_id, target_id)
    copy = AnalysisTarget(
        owner_user_id=owner_user_id,
        name=name.strip(),
        platform=source.platform,
        source_url=source.source_url,
    )
    session.add(copy)
    session.flush()

    reviews = list(
        session.scalars(
            select(Review)
            .where(Review.analysis_target_id == source.id, Review.is_current.is_(True))
            .order_by(Review.reviewed_at.desc().nullslast(), Review.created_at.desc())
        )
    )
    if reviews:
        now = datetime.now(UTC)
        run = IngestionRun(
            analysis_target_id=copy.id,
            status=IngestionStatus.SUCCEEDED.value,
            source_kind=IngestionSourceKind.FILE_IMPORT.value,
            reviews_ingested=len(reviews),
            reviews_rejected=0,
            started_at=now,
            completed_at=now,
        )
        session.add(run)
        session.flush()
        session.add_all(
            Review(
                analysis_target_id=copy.id,
                ingestion_run_id=run.id,
                review_identity_key=review.review_identity_key,
                is_current=True,
                review_text=review.review_text,
                rating=review.rating,
                source_review_id=review.source_review_id,
                reviewer_name=review.reviewer_name,
                reviewed_at=review.reviewed_at,
                review_url=review.review_url,
                source_metadata=review.source_metadata,
            )
            for review in reviews
        )

    session.commit()
    session.refresh(copy)
    return copy


def delete_target(
    session: Session, owner_user_id: uuid.UUID, target_id: uuid.UUID
) -> None:
    target = get_owned_target(session, owner_user_id, target_id)
    session.delete(target)
    session.commit()
