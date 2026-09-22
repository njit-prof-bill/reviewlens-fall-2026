"""Sprint 3 current review dataset semantics.

Revision ID: 20260921_0004
Revises: 20260905_0003
Create Date: 2026-09-21 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0004"
down_revision: str | None = "20260905_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reviews",
        sa.Column("review_identity_key", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "reviews",
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )
    op.execute("""
        UPDATE reviews
        SET review_identity_key = COALESCE(
            'source:' || lower(source_review_id),
            'legacy:' || id::text
        )
        WHERE review_identity_key IS NULL
        """)
    op.alter_column("reviews", "review_identity_key", nullable=False)
    op.create_unique_constraint(
        "uq_reviews_analysis_target_identity",
        "reviews",
        ["analysis_target_id", "review_identity_key"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_reviews_analysis_target_identity", "reviews", type_="unique")
    op.drop_column("reviews", "is_current")
    op.drop_column("reviews", "review_identity_key")
