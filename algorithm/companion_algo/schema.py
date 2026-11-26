"""算法输入数据结构 —— 与成员 C（后端）约定的数据契约。

字段命名严格遵循团队统一约定：
    user_id, check_in_at, activity_type, recorded_at,
    data_source, sync_status, feedback_type, event_status

后端只需把这些表的数据整理成一个 dict 传进来；算法不直接访问数据库。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckIn:
    check_in_at: str
    mood: str = "normal"             # good / normal / unwell / need_help
    status: str = "normal"           # 本人主观状态
    note: str = ""
    data_source: str = "manual"      # manual / watch / simulated_watch
    sync_status: str = "synced"      # synced / pending / failed
    confirmed: bool = True           # 是否经过本人确认

    @classmethod
    def from_dict(cls, d: dict) -> "CheckIn":
        return cls(
            check_in_at=d.get("check_in_at") or d.get("checkin_at") or "",
            mood=d.get("mood", "normal"),
            status=d.get("status", "normal"),
            note=d.get("note", ""),
            data_source=d.get("data_source", "manual"),
            sync_status=d.get("sync_status", "synced"),
            confirmed=bool(d.get("confirmed", True)),
        )


@dataclass
class Activity:
    activity_type: str               # 起床 / 外出 / 回家 / 用餐 / 运动 / 休息 / 服药 / 其他
    recorded_at: str
    note: str = ""
    data_source: str = "manual"
    sync_status: str = "synced"

    @classmethod
    def from_dict(cls, d: dict) -> "Activity":
        return cls(
            activity_type=d.get("activity_type", "其他"),
            recorded_at=d.get("recorded_at") or d.get("created_at") or "",
            note=d.get("note", ""),
            data_source=d.get("data_source", "manual"),
            sync_status=d.get("sync_status", "synced"),
        )


@dataclass
class HealthRecord:
    metric: str                      # steps / heart_rate / sleep，第一版只用 steps
    value: float
    collected_at: str                # 采集时间
    uploaded_at: str | None = None   # 上传时间，未上传为 None
    data_source: str = "simulated_watch"
    valid: bool = True               # 数据有效状态
    sync_status: str = "synced"

    @classmethod
    def from_dict(cls, d: dict) -> "HealthRecord":
        return cls(
            metric=d.get("metric", "steps"),
            value=float(d.get("value", 0)),
            collected_at=d.get("collected_at", ""),
            uploaded_at=d.get("uploaded_at"),
            data_source=d.get("data_source", "simulated_watch"),
            valid=bool(d.get("valid", True)),
            sync_status=d.get("sync_status", "synced"),
        )


@dataclass
class DeviceState:
    device_id: str
    is_online: bool
    last_seen_at: str | None = None
    data_source: str = "simulated_watch"

    @classmethod
    def from_dict(cls, d: dict) -> "DeviceState":
        return cls(
            device_id=d.get("device_id", "unknown"),
            is_online=bool(d.get("is_online", False)),
            last_seen_at=d.get("last_seen_at"),
            data_source=d.get("data_source", "simulated_watch"),
        )


@dataclass
class Feedback:
    feedback_type: str               # 见 rules.py 中的枚举值
    created_at: str
    note: str = ""
    share_with_family: bool = False  # 本人是否授权家属看到这条反馈

    @classmethod
    def from_dict(cls, d: dict) -> "Feedback":
        return cls(
            feedback_type=d.get("feedback_type", ""),
            created_at=d.get("created_at") or d.get("created_time") or "",
            note=d.get("note", ""),
            share_with_family=bool(d.get("share_with_family", False)),
        )


@dataclass
class Authorization:
    family_user_id: int
    status: str = "active"           # active / revoked
    scope: list[str] = field(default_factory=lambda: ["status"])
    can_receive_alerts: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Authorization":
        return cls(
            family_user_id=int(d.get("family_user_id", 0)),
            status=d.get("status", "active"),
            scope=list(d.get("scope") or []),
            can_receive_alerts=bool(d.get("can_receive_alerts", False)),
        )


@dataclass
class AnalysisInput:
    """一次分析的完整输入。"""
    user_id: int
    as_of: str                       # 分析基准时刻（UTC）
    checkins: list[CheckIn] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    health_records: list[HealthRecord] = field(default_factory=list)
    device_states: list[DeviceState] = field(default_factory=list)
    feedbacks: list[Feedback] = field(default_factory=list)
    authorizations: list[Authorization] = field(default_factory=list)
    simulated: bool = True           # 是否模拟数据；必须在展示层明确标注
    config: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisInput":
        return cls(
            user_id=int(data.get("user_id", 0)),
            as_of=data.get("as_of") or "",
            checkins=[CheckIn.from_dict(d) for d in (data.get("checkins") or [])],
            activities=[Activity.from_dict(d) for d in (data.get("activities") or [])],
            health_records=[HealthRecord.from_dict(d) for d in (data.get("health_records") or [])],
            device_states=[DeviceState.from_dict(d) for d in (data.get("device_states") or [])],
            feedbacks=[Feedback.from_dict(d) for d in (data.get("feedbacks") or [])],
            authorizations=[Authorization.from_dict(d) for d in (data.get("authorizations") or [])],
            simulated=bool(data.get("simulated", True)),
            config=dict(data.get("config") or {}),
        )
