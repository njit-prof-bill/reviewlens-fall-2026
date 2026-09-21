import csv
import re
import uuid
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import AnalysisTarget, QAEntry, Review
from app.services import review_service


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "analysis"


def reviews_csv_filename(target: AnalysisTarget) -> str:
    return f"{_slug(target.name)}-reviews.csv"


def analysis_markdown_filename(target: AnalysisTarget) -> str:
    return f"{_slug(target.name)}-analysis.md"


def current_reviews(session: Session, target_id: uuid.UUID) -> list[Review]:
    statement = (
        select(Review)
        .where(Review.analysis_target_id == target_id, Review.is_current.is_(True))
        .order_by(Review.reviewed_at.desc().nullslast(), Review.created_at.desc())
    )
    return list(session.scalars(statement))


def build_reviews_csv(session: Session, target: AnalysisTarget) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "analysis_name",
            "source_url",
            "rating",
            "reviewed_at",
            "reviewer_name",
            "review_text",
            "source_review_id",
            "review_url",
        ]
    )
    for review in current_reviews(session, target.id):
        writer.writerow(
            [
                target.name,
                target.source_url,
                review.rating,
                review.reviewed_at.isoformat() if review.reviewed_at else "",
                review.reviewer_name or "",
                review.review_text,
                review.source_review_id or "",
                review.review_url or "",
            ]
        )
    return buffer.getvalue()


def build_analysis_markdown(session: Session, target: AnalysisTarget) -> str:
    summary = review_service.build_summary(session, target)
    questions = list(
        session.scalars(
            select(QAEntry)
            .options(selectinload(QAEntry.evidence))
            .where(QAEntry.analysis_target_id == target.id)
            .order_by(QAEntry.created_at, QAEntry.id)
        )
    )
    lines = [
        f"# {target.name}",
        "",
        f"- Platform: {target.platform}",
        f"- Source URL: {target.source_url}",
        f"- Reviews collected: {summary['reviews_collected']}",
        f"- Average rating: {summary['average_rating'] or 'Not available'}",
        f"- Earliest review: {summary['earliest_review'] or 'Not available'}",
        f"- Latest review: {summary['latest_review'] or 'Not available'}",
        "",
        "## Q&A History",
        "",
    ]
    if not questions:
        lines.append("No Q&A history has been saved for this analysis.")
        return "\n".join(lines) + "\n"

    for entry in questions:
        lines.extend(
            [
                "### Question",
                "",
                entry.question,
                "",
                "### Analysis",
                "",
                entry.answer,
                "",
            ]
        )
        if entry.evidence:
            lines.extend(["Supporting evidence:", ""])
            for evidence in entry.evidence:
                reviewer = evidence.reviewer_name or "Reviewer"
                rating = f", {evidence.rating:.1f} stars" if evidence.rating else ""
                lines.append(f"> {evidence.excerpt}")
                lines.append(f"> — {reviewer}{rating}")
                lines.append("")
    return "\n".join(lines) + "\n"
