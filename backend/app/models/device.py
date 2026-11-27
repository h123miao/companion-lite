"""device_bindings 表：设备绑定表。"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class DeviceBinding(Base):
    __tablename__ = "device_bindings"
    __table_args__ = (
        UniqueConstraint("user_id", "device_id", name="uq_user_device"),
        Index("ix_device_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    device_type: Mapped[str] = mapped_column(String(30), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    bound_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    unbound_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
