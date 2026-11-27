"""设备/健康数据/同步日志相关模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

DEVICE_TYPES = {"xiaomi_watch", "other"}
DATA_TYPES = {"steps", "heart_rate", "sleep", "activity_duration"}
HEALTH_UNITS = {"steps": "steps", "heart_rate": "bpm", "sleep": "minutes", "activity_duration": "minutes"}
DATA_SOURCES = {"manual", "device"}
SYNC_STATUSES = {"synced", "pending", "failed"}
SYNC_LOG_STATUSES = {"success", "failed", "pending"}


class DeviceCreate(BaseModel):
    device_type: str = Field(description="xiaomi_watch/other")
    device_id: str = Field(min_length=1, max_length=100)
    device_name: str | None = Field(default=None, max_length=100)


class DeviceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_type: str
    device_id: str
    device_name: str | None = None
    status: str
    last_seen_at: datetime | None = None
    bound_at: datetime


class DeviceStatusUpdate(BaseModel):
    status: str = Field(description="active/offline/unbound")


class HealthRecordCreate(BaseModel):
    data_type: str = Field(description="steps/heart_rate/sleep/activity_duration")
    value: float = Field(ge=0)
    device_binding_id: int | None = None
    collected_at: datetime
    uploaded_at: datetime | None = None
    data_source: str = Field(default="device")
    sync_status: str = Field(default="synced")


class HealthRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_binding_id: int | None = None
    data_type: str
    value: float
    unit: str
    collected_at: datetime
    uploaded_at: datetime | None = None
    data_source: str
    sync_status: str
    is_valid: bool
    is_confirmed: bool
    created_at: datetime


class SyncLogCreate(BaseModel):
    sync_type: str
    status: str = Field(description="success/failed/pending")
    device_binding_id: int | None = None
    started_at: datetime
    finished_at: datetime | None = None
    records_count: int = Field(default=0, ge=0)
    error_message: str | None = Field(default=None, max_length=500)


class SyncLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_binding_id: int | None = None
    sync_type: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    records_count: int
    error_message: str | None = None
