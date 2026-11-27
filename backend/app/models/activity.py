"""activity_records 表：活动记录表。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class ActivityRecord(Base):
    __tablename__ = "activity_records"
    __table_args__ = (Index("ix_activity_user_time", "user_id", "recorded_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    activity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    sync_status: Mapped[str] = mapped_column(String(20), nullable=False, default="synced")
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
