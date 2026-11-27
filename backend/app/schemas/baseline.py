"""基线与看板相关模型。"""

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict


class BaselineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    window_days: int
    checkin_time_median: time | None = None
    checkin_time_mean: time | None = None
    checkin_time_stddev: float | None = None
    checkin_iqr_min: time | None = None
    checkin_iqr_max: time | None = None
    avg_daily_activities: float | None = None
    avg_weekly_activities: float | None = None
    avg_daily_steps: float | None = None
    feedback_distribution: str | None = None
    valid_days: int
    data_sufficient: bool
    calculated_at: datetime


class DataStatus(BaseModel):
    """数据可信度状态（简化版，供看板展示）。"""

    device_status: str  # active/offline/unbound
    last_sync_status: str  # success/failed/pending/none
    data_sufficient: bool
    note: str
