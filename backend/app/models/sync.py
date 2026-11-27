"""data_sync_logs 表：数据同步日志表。

用于区分设备离线、同步延迟和数据缺失三种不同情况。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class DataSyncLog(Base):
    __tablename__ = "data_sync_logs"
    __table_args__ = (Index("ix_sync_user_time", "user_id", "started_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    device_binding_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("device_bindings.id", ondelete="RESTRICT"), nullable=True
    )
    sync_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    records_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
