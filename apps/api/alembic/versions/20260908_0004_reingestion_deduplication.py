"""Add idempotent re-ingestion metadata.

Revision ID: 20260908_0004
Revises: 20260905_0003
Create Date: 2026-09-08 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260908_0004"
down_revision: str | None = "20260905_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingestion_runs",
        sa.Column(
            "reviews_duplicate", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "reviews", sa.Column("dedupe_key", sa.String(length=64), nullable=True)
    )
    op.create_index(
        "ix_reviews_analysis_target_dedupe_key",
        "reviews",
        ["analysis_target_id", "dedupe_key"],
    )
    op.create_unique_constraint(
        "uq_reviews_analysis_target_dedupe_key",
        "reviews",
        ["analysis_target_id", "dedupe_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_reviews_analysis_target_dedupe_key", "reviews", type_="unique"
    )
    op.drop_index("ix_reviews_analysis_target_dedupe_key", table_name="reviews")
    op.drop_column("reviews", "dedupe_key")
    op.drop_column("ingestion_runs", "reviews_duplicate")
