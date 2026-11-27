"""family_links 表：家庭关系及授权表。

这是整个项目的数据安全核心：家属能否访问本人数据，全看这张表。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class FamilyLink(Base):
    __tablename__ = "family_links"
    __table_args__ = (
        UniqueConstraint("owner_id", "family_id", name="uq_owner_family"),
        Index("ix_family_owner_status", "owner_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    family_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    invite_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    relation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # permission_scope: JSON 数组字符串，如 ["checkins","activities","care_events"]
    permission_scope: Mapped[str | None] = mapped_column(String(500), nullable=True)
    can_receive_alert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
