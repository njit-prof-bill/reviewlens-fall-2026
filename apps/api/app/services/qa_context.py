import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Review


@dataclass(frozen=True, slots=True)
class QAContext:
    text: str
    reviews: tuple[Review, ...]
    available_review_count: int


def build_context(
    session: Session, target_id: uuid.UUID, max_characters: int
) -> QAContext:
    statement = (
        select(Review)
        .where(Review.analysis_target_id == target_id)
        .order_by(Review.reviewed_at.desc().nullslast(), Review.id)
    )
    available = tuple(session.scalars(statement))
    included: list[Review] = []
    blocks: list[str] = []
    used = 0

    for review in available:
        block = (
            f"[review_id={review.id}]\n"
            f"rating={review.rating}\n"
            f"date={review.reviewed_at.isoformat() if review.reviewed_at else 'unknown'}\n"
            f"text={review.review_text}\n"
        )
        if blocks and used + len(block) > max_characters:
            break
        blocks.append(block[:max_characters] if not blocks else block)
        included.append(review)
        used += len(blocks[-1])

    return QAContext(
        text="\n".join(blocks),
        reviews=tuple(included),
        available_review_count=len(available),
    )
