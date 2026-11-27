"""签到相关的请求/响应模型。字段命名严格遵循团队统一约定。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

MOOD_VALUES = {"good", "normal", "uncomfortable", "need_help"}
STATUS_VALUES = {"normal", "good", "uncomfortable", "need_help"}
DATA_SOURCES = {"manual", "device"}
SYNC_STATUSES = {"synced", "pending", "failed"}


class CheckinCreate(BaseModel):
    """提交签到请求。check_in_at 由客户端提供，必须是 UTC 时间（带 Z 后缀或 +00:00）。"""

    check_in_at: datetime
    mood: str | None = Field(default=None, description="good/normal/uncomfortable/need_help")
    status: str = Field(default="normal", description="normal/good/uncomfortable/need_help")
    note: str | None = Field(default=None, max_length=500)
    data_source: str = Field(default="manual", description="manual/device")
    sync_status: str = Field(default="synced", description="synced/pending")


class CheckinOut(BaseModel):
    """签到响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    check_in_at: datetime
    mood: str | None = None
    status: str
    note: str | None = None
    data_source: str
    sync_status: str
    is_confirmed: bool
    created_at: datetime
