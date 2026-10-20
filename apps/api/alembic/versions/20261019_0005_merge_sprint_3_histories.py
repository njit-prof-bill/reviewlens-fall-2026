"""Reconcile the original and replacement Sprint 3 migration histories."""

from collections.abc import Sequence

revision: str = "20261019_0005"
down_revision: tuple[str, str] = ("20260908_0004", "20260921_0004")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
