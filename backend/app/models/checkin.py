"""daily_checkins 表：每日签到表。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class DailyCheckin(Base):
    __tablename__ = "daily_checkins"
    __table_args__ = (
        Index("ix_checkin_user_time", "user_id", "check_in_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    check_in_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    mood: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    sync_status: Mapped[str] = mapped_column(String(20), nullable=False, default="synced")
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
