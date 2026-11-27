"""user_feedback 表：用户反馈表。"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    __table_args__ = (Index("ix_feedback_user_time", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    care_event_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("care_events.id", ondelete="RESTRICT"), nullable=True
    )
    feedback_type: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
