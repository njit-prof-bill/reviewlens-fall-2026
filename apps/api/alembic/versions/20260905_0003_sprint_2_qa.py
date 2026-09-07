"""Sprint 2 ingestion details and persisted review Q&A.

Revision ID: 20260905_0003
Revises: 20260904_0002
Create Date: 2026-09-05 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260905_0003"
down_revision: str | None = "20260904_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingestion_runs",
        sa.Column("rejection_reasons", sa.JSON(), nullable=True),
    )

    op.create_table(
        "qa_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("result_kind", sa.String(length=40), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("context_review_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["analysis_target_id"], ["analysis_targets.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_qa_entries_analysis_target_id",
        "qa_entries",
        ["analysis_target_id"],
    )

    op.create_table(
        "qa_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("qa_entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("reviewer_name", sa.String(length=255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["qa_entry_id"], ["qa_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("qa_entry_id", "position"),
    )
    op.create_index("ix_qa_evidence_qa_entry_id", "qa_evidence", ["qa_entry_id"])
    op.create_index("ix_qa_evidence_review_id", "qa_evidence", ["review_id"])


def downgrade() -> None:
    op.drop_index("ix_qa_evidence_review_id", table_name="qa_evidence")
    op.drop_index("ix_qa_evidence_qa_entry_id", table_name="qa_evidence")
    op.drop_table("qa_evidence")
    op.drop_index("ix_qa_entries_analysis_target_id", table_name="qa_entries")
    op.drop_table("qa_entries")
    op.drop_column("ingestion_runs", "rejection_reasons")
