import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.session import Base


class AnalysisTarget(Base):
    """A user-owned entity under review, identified by its review-platform URL."""

    __tablename__ = "analysis_targets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner = relationship("User")
    reviews = relationship(
        "Review", back_populates="analysis_target", cascade="all, delete-orphan"
    )
    ingestion_runs = relationship(
        "IngestionRun", back_populates="analysis_target", cascade="all, delete-orphan"
    )
    qa_entries = relationship(
        "QAEntry", back_populates="analysis_target", cascade="all, delete-orphan"
    )
