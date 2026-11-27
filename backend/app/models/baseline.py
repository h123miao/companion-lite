"""baseline_profiles 表：个人生活基线表。"""

from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class BaselineProfile(Base):
    __tablename__ = "baseline_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    window_days: Mapped[int] = mapped_column(Integer, nullable=False, default=14)
    checkin_time_median: Mapped[time | None] = mapped_column(Time, nullable=True)
    checkin_time_mean: Mapped[time | None] = mapped_column(Time, nullable=True)
    checkin_time_stddev: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    checkin_iqr_min: Mapped[time | None] = mapped_column(Time, nullable=True)
    checkin_iqr_max: Mapped[time | None] = mapped_column(Time, nullable=True)
    avg_daily_activities: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    avg_weekly_activities: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    avg_daily_steps: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    feedback_distribution: Mapped[str | None] = mapped_column(String(500), nullable=True)
    valid_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_sufficient: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
