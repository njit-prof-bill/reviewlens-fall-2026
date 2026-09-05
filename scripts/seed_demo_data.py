#!/usr/bin/env python
"""Seed the two demo accounts required by the Sprint 1 demo script.

The demo expects meaningful persisted data before the clock starts: User A with
two or more targets and one dataset of 15-20+ reviews, User B with one target
and a smaller, clearly distinct dataset.

Reviews come from files you supply, so the seeded data is real collected review
data rather than fabricated records. Export them once from the live provider,
keep them out of source control, then re-seed on any machine.

Usage:
    python scripts/seed_demo_data.py \
        --user-a-clerk-id user_2abc... --user-a-email a@example.com \
        --user-b-clerk-id user_2def... --user-b-email b@example.com \
        --user-a-reviews ~/demo/blue-bottle.json \
        --user-b-reviews ~/demo/downtown-hotel.json

Re-running is safe: targets are matched by owner and source URL.
"""

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from sqlalchemy import select  # noqa: E402

from app.db.models import AnalysisTarget, IngestionRun, Review, User  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.domain import IngestionSourceKind, IngestionStatus  # noqa: E402
from app.services.ingestion.normalizer import normalize_all  # noqa: E402
from app.services.ingestion.sources.file_import import parse_upload  # noqa: E402
from app.services.source_url import validate_source_url  # noqa: E402

DEFAULT_A_URL = (
    "https://www.google.com/maps/place/Blue+Bottle+Coffee/"
    "@37.7823,-122.4074,17z/data=!4m6!3m5!1s0x8085808f0b0b0b0b:0x1234abcd"
)
DEFAULT_A_SECOND_URL = (
    "https://www.google.com/maps/place/Tartine+Bakery/"
    "@37.7614,-122.4241,17z/data=!4m6!3m5!1s0x8085809c1c1c1c1c:0x5678ef01"
)
DEFAULT_B_URL = (
    "https://www.google.com/maps/place/Downtown+Hotel/"
    "@40.7128,-74.0060,17z/data=!4m6!3m5!1s0x89c25a1b1b1b1b1b:0x9abc2345"
)


def get_or_create_user(session, clerk_id: str, email: str, display_name: str) -> User:
    user = session.scalars(
        select(User).where(User.auth_provider_user_id == clerk_id)
    ).one_or_none()
    if user:
        return user

    user = User(
        auth_provider="clerk",
        auth_provider_user_id=clerk_id,
        email=email,
        display_name=display_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_or_create_target(session, owner: User, name: str, source_url: str):
    validate_source_url(source_url)
    target = session.scalars(
        select(AnalysisTarget).where(
            AnalysisTarget.owner_user_id == owner.id,
            AnalysisTarget.source_url == source_url,
        )
    ).one_or_none()
    if target:
        return target

    target = AnalysisTarget(
        owner_user_id=owner.id,
        name=name,
        platform="google_maps",
        source_url=source_url,
    )
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def load_reviews(session, target: AnalysisTarget, review_file: Path) -> int:
    existing = session.scalars(
        select(Review).where(Review.analysis_target_id == target.id).limit(1)
    ).one_or_none()
    if existing:
        print(f"  reviews already present for {target.name}; skipping")
        return 0

    accepted, rejected = normalize_all(
        parse_upload(review_file.name, review_file.read_bytes())
    )
    if not accepted:
        raise SystemExit(f"No usable reviews found in {review_file}")

    now = datetime.now(timezone.utc)
    run = IngestionRun(
        analysis_target_id=target.id,
        status=(
            IngestionStatus.PARTIAL.value
            if rejected
            else IngestionStatus.SUCCEEDED.value
        ),
        source_kind=IngestionSourceKind.FILE_IMPORT.value,
        reviews_ingested=len(accepted),
        reviews_rejected=len(rejected),
        started_at=now,
        completed_at=now,
    )
    session.add(run)
    session.commit()
    session.refresh(run)

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
    return len(accepted)


def warn_if_thin(label: str, count: int, minimum: int) -> None:
    if 0 < count < minimum:
        print(
            f"  WARNING: {label} has only {count} reviews; the demo expects {minimum}+"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-a-clerk-id", required=True)
    parser.add_argument("--user-a-email", required=True)
    parser.add_argument("--user-b-clerk-id", required=True)
    parser.add_argument("--user-b-email", required=True)
    parser.add_argument("--user-a-reviews", type=Path, required=True)
    parser.add_argument("--user-b-reviews", type=Path, required=True)
    parser.add_argument("--user-a-url", default=DEFAULT_A_URL)
    parser.add_argument("--user-a-second-url", default=DEFAULT_A_SECOND_URL)
    parser.add_argument("--user-b-url", default=DEFAULT_B_URL)
    parser.add_argument("--user-a-name", default="Blue Bottle Coffee - Mint Plaza")
    parser.add_argument("--user-a-second-name", default="Tartine Bakery")
    parser.add_argument("--user-b-name", default="Downtown Hotel")
    args = parser.parse_args()

    for path in (args.user_a_reviews, args.user_b_reviews):
        if not path.exists():
            raise SystemExit(f"Review file not found: {path}")

    session = SessionLocal()
    try:
        user_a = get_or_create_user(
            session, args.user_a_clerk_id, args.user_a_email, "Demo User A"
        )
        user_b = get_or_create_user(
            session, args.user_b_clerk_id, args.user_b_email, "Demo User B"
        )

        print(f"User A: {user_a.id}")
        target_a = get_or_create_target(
            session, user_a, args.user_a_name, args.user_a_url
        )
        count_a = load_reviews(session, target_a, args.user_a_reviews)
        warn_if_thin(args.user_a_name, count_a, 15)
        # A second target proves the list is populated, not a single lucky record.
        get_or_create_target(
            session, user_a, args.user_a_second_name, args.user_a_second_url
        )

        print(f"User B: {user_b.id}")
        target_b = get_or_create_target(
            session, user_b, args.user_b_name, args.user_b_url
        )
        count_b = load_reviews(session, target_b, args.user_b_reviews)
        warn_if_thin(args.user_b_name, count_b, 5)

        print("\nCross-user demo target (request this id while signed in as User B):")
        print(f"  /analysis/{target_a.id}")
        print(f"  GET /api/v1/analysis-targets/{target_a.id}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
