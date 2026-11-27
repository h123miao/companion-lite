"""health_records 表：穿戴设备数据表。

重要：本表数据缺失不能推断为用户没有活动。
可信度判断由算法模块基于 data_source/sync_status/is_valid 等字段完成。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time_utils import utcnow
from app.database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"
    __table_args__ = (Index("ix_health_user_type_time", "user_id", "data_type", "collected_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    device_binding_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("device_bindings.id", ondelete="RESTRICT"), nullable=True
    )
    data_type: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    data_source: Mapped[str] = mapped_column(String(30), nullable=False, default="device")
    sync_status: Mapped[str] = mapped_column(String(20), nullable=False, default="synced")
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
