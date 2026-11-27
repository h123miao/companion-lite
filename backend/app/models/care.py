"""care_events 表：关怀事件表。

状态机：pending -> asking -> answered -> family_pending -> closed
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class CareEvent(Base):
    __tablename__ = "care_events"
    __table_args__ = (
        Index("ix_care_user_status", "user_id", "event_status"),
        Index("ix_care_family", "family_link_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    family_link_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("family_links.id", ondelete="RESTRICT"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_emergency: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trigger_rule: Mapped[str] = mapped_column(String(50), nullable=False)
    event_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    concern_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    asked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user_response: Mapped[str | None] = mapped_column(String(30), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    family_notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    family_contacted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    handled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
