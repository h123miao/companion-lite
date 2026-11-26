"""核心算法二：数据可信度判断（Data Credibility）。

这是项目最重要的创新点之一。系统在"分析生活变化"之前，先判断数据
本身是否可靠，避免把"没收到数据"误解成"用户有危险"或"用户没活动"。

六种状态（与项目说明书一致）：
    normal           正常记录
    missing_unknown  数据缺失，原因未知
    device_offline   设备离线，已确认
    sync_delay       数据同步延迟
    user_feedback    用户主动反馈（本人的表述优先于设备数据）
    insufficient     数据不足，暂时不能分析

优先级：user_feedback > device_offline > sync_delay > normal > missing_unknown
insufficient 是独立标志，会直接阻止变化识别输出结论。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from .baseline import BaselineResult
from .rules import DEFAULT_CONFIG
from .schema import AnalysisInput
from .utils import iso_utc, local_day, parse_time


@dataclass
class CredibilityReport:
    overall_status: str
    checkin_status: str
    device_status: str
    health_status: str
    insufficient: bool
    reasons: list[str] = field(default_factory=list)
    source_details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "overall_status": self.overall_status,
            "checkin_status": self.checkin_status,
            "device_status": self.device_status,
            "health_status": self.health_status,
            "insufficient": self.insufficient,
            "reasons": self.reasons,
            "source_details": self.source_details,
        }


def assess_credibility(
    inp: AnalysisInput,
    baseline: BaselineResult,
    config: dict | None = None,
) -> CredibilityReport:
    """评估"今天"的数据可信度。"""
    cfg = {**DEFAULT_CONFIG, **(config or inp.config or {})}
    offset = float(cfg["timezone_offset_hours"])
    as_of = parse_time(inp.as_of)
    reasons: list[str] = []
    details: dict = {}

    if as_of is None:
        return CredibilityReport(
            overall_status="insufficient",
            checkin_status="missing_unknown",
            device_status="device_offline",
            health_status="missing_unknown",
            insufficient=True,
            reasons=["分析基准时间无效，暂不判断"],
        )

    today = local_day(as_of, offset)

    # ---- 1. 今日签到 ----
    today_checkins = [
        c for c in inp.checkins
        if (t := parse_time(c.check_in_at)) is not None and local_day(t, offset) == today
    ]
    if today_checkins:
        pending = [c for c in today_checkins if c.sync_status == "pending"]
        if pending:
            checkin_status = "sync_delay"
            reasons.append("今日签到已记录，但同步状态为 pending，数据尚未完全上传")
        else:
            checkin_status = "normal"
            reasons.append("今日已收到本人签到记录")
        details["checkin"] = {
            "count": len(today_checkins),
            "latest_at": iso_utc(parse_time(today_checkins[-1].check_in_at)),
            "source": today_checkins[-1].data_source,
        }
    else:
        checkin_status = "missing_unknown"
        reasons.append("今日尚未收到签到记录，原因未知（不等于用户有危险）")
        details["checkin"] = {"count": 0, "latest_at": None}

    # ---- 2. 设备状态 ----
    devices = inp.device_states
    online = [d for d in devices if d.is_online]
    if not devices:
        device_status = "missing_unknown"
        reasons.append("没有可用的设备在线状态信息，无法判断设备是否离线")
    elif online:
        device_status = "normal"
        reasons.append(f"{len(online)} 台设备在线")
    else:
        device_status = "device_offline"
        reasons.append("已确认所有绑定设备离线，设备数据缺失不能解释为用户没有活动")
    details["device"] = {
        "total": len(devices),
        "online": len(online),
        "device_ids": [d.device_id for d in devices],
    }

    # ---- 3. 穿戴设备数据同步 ----
    recent_cutoff = as_of - timedelta(days=1)
    recent_health = [
        h for h in inp.health_records
        if (t := parse_time(h.collected_at)) is not None and t >= recent_cutoff
    ]
    pending_health = [
        h for h in recent_health
        if h.sync_status in {"pending", "failed"} or h.uploaded_at is None
    ]
    invalid_health = [h for h in recent_health if not h.valid]
    if pending_health:
        health_status = "sync_delay"
        reasons.append(
            f"最近 24 小时有 {len(pending_health)} 条穿戴数据未成功上传，"
            "不能据此判断用户活动减少"
        )
    elif recent_health and not invalid_health:
        health_status = "normal"
        reasons.append("最近 24 小时穿戴数据已同步完成")
    elif invalid_health:
        health_status = "missing_unknown"
        reasons.append("最近 24 小时存在无效穿戴数据，已排除，不作为判断依据")
    else:
        health_status = "missing_unknown"
        reasons.append("最近 24 小时没有收到穿戴数据，原因未知")
    details["health"] = {
        "records_24h": len(recent_health),
        "pending": len(pending_health),
        "invalid": len(invalid_health),
        "note": "手表数据为模拟数据时必须在展示层标注，不得称为真实设备采集",
    }

    # ---- 4. 用户主动反馈：本人表述优先级最高 ----
    recent_feedbacks = [
        f for f in inp.feedbacks
        if (t := parse_time(f.created_at)) is not None and t >= recent_cutoff
    ]
    if recent_feedbacks:
        latest = max(recent_feedbacks, key=lambda f: parse_time(f.created_at))
        reasons.append(
            f"本人于 {iso_utc(parse_time(latest.created_at))} 主动反馈 "
            f"{latest.feedback_type}，本人的明确表述优先于设备推断"
        )
        details["feedback"] = {
            "latest_type": latest.feedback_type,
            "latest_at": iso_utc(parse_time(latest.created_at)),
            "share_with_family": latest.share_with_family,
        }
        overall = "user_feedback"
    else:
        # 普通情况下的整体状态：按优先级取最"确定"的一种
        if checkin_status == "normal":
            overall = "normal"
        elif device_status == "device_offline":
            overall = "device_offline"
        elif health_status == "sync_delay" or checkin_status == "sync_delay":
            overall = "sync_delay"
        else:
            overall = checkin_status

    # ---- 5. 基线数据不足：独立阻断标志 ----
    insufficient = not baseline.sufficient
    if insufficient:
        reasons.append(baseline.insufficient_reason or "数据不足，暂不判断")
        overall = "insufficient"

    return CredibilityReport(
        overall_status=overall,
        checkin_status=checkin_status,
        device_status=device_status,
        health_status=health_status,
        insufficient=insufficient,
        reasons=reasons,
        source_details=details,
    )
