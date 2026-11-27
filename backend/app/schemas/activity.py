"""活动记录相关请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

ACTIVITY_TYPES = {
    "wake_up", "go_out", "go_home", "meal", "exercise", "rest", "medication", "other"
}
DATA_SOURCES = {"manual", "device"}
SYNC_STATUSES = {"synced", "pending", "failed"}


class ActivityCreate(BaseModel):
    activity_type: str = Field(description="wake_up/go_out/go_home/meal/exercise/rest/medication/other")
    recorded_at: datetime
    note: str | None = Field(default=None, max_length=500)
    data_source: str = Field(default="manual")
    sync_status: str = Field(default="synced")


class ActivityUpdate(BaseModel):
    """修改活动记录，所有字段可选。"""

    activity_type: str | None = None
    recorded_at: datetime | None = None
    note: str | None = None


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    activity_type: str
    recorded_at: datetime
    note: str | None = None
    data_source: str
    sync_status: str
    is_confirmed: bool
    created_at: datetime
