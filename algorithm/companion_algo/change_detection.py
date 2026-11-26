"""核心算法三：生活变化识别（Change Detection）。

五条规则全部基于"本人自己的历史规律"，每条结果都记录：
识别时间、触发规则、使用的数据、数据状态、生成原因。
只看"完整自然日"，今天尚未结束时不计入连续漏签到，减少误报。

注意：confidence 是规则置信度，不是医疗风险概率，展示时必须标注。
"""

from __future__ import annotations

from datetime import timedelta

from .baseline import BaselineResult
from .credibility import CredibilityReport
from .rules import (
    CONTACT_REQUEST_FEEDBACK,
    DEFAULT_CONFIG,
    NEGATIVE_FEEDBACK_TYPES,
    RULE_META,
)
from .schema import AnalysisInput
from .utils import (
    format_minutes,
    iso_utc,
    local_day,
    mean_or_none,
    minutes_of_day,
    normalize_minutes,
    parse_time,
)


def _result(
    rule_id: str,
    reason: str,
    data_used: dict,
    data_status: str,
    confidence: float,
    as_of_iso: str,
    severity: str = "attention",
) -> dict:
    meta = RULE_META[rule_id]
    return {
        "rule_id": rule_id,
        "rule_name": meta["name"],
        "rule_description": meta["description"],
        "detected_at": as_of_iso,
        "severity": severity,
        "reason": reason,
        "data_used": data_used,
        "data_status": data_status,
        "confidence": confidence,
        "confidence_note": "规则置信度，非医疗风险概率",
        "event_status": "detected",
    }


def detect_changes(
    inp: AnalysisInput,
    baseline: BaselineResult,
    credibility: CredibilityReport,
    config: dict | None = None,
) -> dict:
    """返回 {"detected": [...], "suppressed": [...]}。"""
    cfg = {**DEFAULT_CONFIG, **(config or inp.config or {})}
    offset = float(cfg["timezone_offset_hours"])
    as_of = parse_time(inp.as_of)
    as_of_iso = iso_utc(as_of)
    detected: list[dict] = []
    suppressed: list[dict] = []

    if as_of is None or not baseline.sufficient or credibility.insufficient:
        reason = baseline.insufficient_reason or "数据不足，暂不判断"
        for rule_id in RULE_META:
            suppressed.append({
                "rule_id": rule_id,
                "rule_name": RULE_META[rule_id]["name"],
                "reason": reason,
            })
        return {"detected": detected, "suppressed": suppressed}

    today = local_day(as_of, offset)
    data_status = credibility.overall_status
    grace = float(cfg["checkin_grace_minutes"])
    window_end = baseline.checkin_window_end

    # ---------- R1：签到时间偏离 ----------
    today_checkins = [
        c for c in inp.checkins
        if (t := parse_time(c.check_in_at)) is not None and local_day(t, offset) == today
    ]
    if today_checkins:
        latest = max(today_checkins, key=lambda c: parse_time(c.check_in_at))
        minute = normalize_minutes(minutes_of_day(parse_time(latest.check_in_at), offset))
        if window_end is not None and minute > window_end + grace:
            detected.append(_result(
                "R1_CHECKIN_TIME_DEVIATION",
                f"今日签到时间为 {format_minutes(minute)}，比本人平时签到区间末端 "
                f"{format_minutes(window_end)} 晚了 {int(minute - window_end)} 分钟"
                "（已超过 30 分钟宽限）。这只是生活规律变化，不代表发生危险。",
                {
                    "today_checkin_at": iso_utc(parse_time(latest.check_in_at)),
                    "typical_checkin_window": [
                        format_minutes(baseline.checkin_window_start),
                        format_minutes(baseline.checkin_window_end),
                    ],
                    "median_checkin_time": format_minutes(baseline.checkin_median_min),
                    "coverage_days": baseline.coverage_days,
                },
                data_status,
                0.75,
                as_of_iso,
            ))
    elif window_end is not None:
        current_minute = normalize_minutes(minutes_of_day(as_of, offset))
        if current_minute > window_end + grace:
            extra = ""
            if data_status in {"device_offline", "sync_delay"}:
                extra = "（当前设备离线或数据同步延迟，可能只是数据未送达）"
            elif data_status == "missing_unknown":
                extra = "（原因未知，不能直接判断为用户发生意外）"
            detected.append(_result(
                "R1_CHECKIN_TIME_DEVIATION",
                f"当前时间 {format_minutes(current_minute)} 已超过本人平时签到区间末端 "
                f"{format_minutes(window_end)}，尚未收到今日签到记录。"
                f"这只是需要确认的生活变化{extra}。",
                {
                    "today_checkin_count": 0,
                    "typical_checkin_window": [
                        format_minutes(baseline.checkin_window_start),
                        format_minutes(baseline.checkin_window_end),
                    ],
                    "median_checkin_time": format_minutes(baseline.checkin_median_min),
                    "credibility_reasons": credibility.reasons,
                },
                data_status,
                0.70,
                as_of_iso,
            ))

    # ---------- R2：活动记录数量变化 ----------
    recent_days = int(cfg["activity_recent_days"])
    baseline_mean = baseline.daily_activity_mean
    if baseline_mean is not None and baseline_mean >= float(cfg["activity_min_baseline"]):
        counts: dict = {}
        for a in inp.activities:
            t = parse_time(a.recorded_at)
            if t is None:
                continue
            day = local_day(t, offset)
            if day < today:
                counts[day] = counts.get(day, 0) + 1
        window_start = today - timedelta(days=recent_days)
        recent_values = [counts.get(window_start + timedelta(days=i), 0)
                         for i in range(recent_days)]
        recent_mean = mean_or_none(recent_values) or 0.0
        threshold = baseline_mean * float(cfg["activity_drop_ratio"])
        if recent_mean <= threshold:
            detected.append(_result(
                "R2_ACTIVITY_COUNT_DROP",
                f"最近 {recent_days} 天平均每天 {recent_mean:.1f} 条活动记录，"
                f"低于本人基线的 {baseline_mean:.1f} 条的 "
                f"{int(float(cfg['activity_drop_ratio']) * 100)}%（{threshold:.1f} 条）。"
                "活动记录减少也可能只是没有手动记录，需先询问本人。",
                {
                    "recent_days": recent_days,
                    "recent_daily_counts": recent_values,
                    "recent_mean": round(recent_mean, 2),
                    "baseline_daily_mean": baseline_mean,
                    "drop_threshold": round(threshold, 2),
                },
                data_status,
                0.60,
                as_of_iso,
            ))

    # ---------- R3：连续漏签到（只看已结束的自然日） ----------
    missing_days: list[str] = []
    checkin_days = set()
    for c in inp.checkins:
        t = parse_time(c.check_in_at)
        if t is not None:
            checkin_days.add(local_day(t, offset))
    day = today - timedelta(days=1)
    for _ in range(int(cfg["baseline_window_days"])):
        if day in checkin_days:
            break
        missing_days.append(day.isoformat())
        day -= timedelta(days=1)
    if len(missing_days) >= int(cfg["consecutive_missing_days"]):
        detected.append(_result(
            "R3_CONSECUTIVE_MISSING_CHECKINS",
            f"连续 {len(missing_days)} 个完整自然日没有收到签到记录"
            f"（{missing_days[-1]} 至 {missing_days[0]}）。"
            "可能原因包括用户忙碌、设备离线或数据未同步，需先询问本人。",
            {
                "missing_dates": list(reversed(missing_days)),
                "consecutive_days": len(missing_days),
                "credibility_reasons": credibility.reasons,
            },
            data_status,
            0.80,
            as_of_iso,
        ))

    # ---------- R4：连续负面反馈 ----------
    feedbacks = [
        f for f in inp.feedbacks
        if parse_time(f.created_at) is not None
    ]
    feedbacks.sort(key=lambda f: parse_time(f.created_at))
    trailing_negative = 0
    for f in reversed(feedbacks):
        if f.feedback_type in NEGATIVE_FEEDBACK_TYPES:
            trailing_negative += 1
        else:
            break
    if trailing_negative >= int(cfg["consecutive_negative_feedback"]):
        detected.append(_result(
            "R4_CONSECUTIVE_NEGATIVE_FEEDBACK",
            f"本人连续 {trailing_negative} 次主动反馈身体不适或需要帮助，"
            "这是本人明确表达，应当关注并按授权情况通知家属。",
            {
                "consecutive_negative_count": trailing_negative,
                "latest_feedback_type": feedbacks[-1].feedback_type,
                "latest_feedback_at": iso_utc(parse_time(feedbacks[-1].created_at)),
            },
            "user_feedback",
            0.85,
            as_of_iso,
            severity="attention",
        ))

    # ---------- R5：本人请求家人联系 ----------
    cutoff = as_of - timedelta(days=1)
    contact_requests = [
        f for f in inp.feedbacks
        if f.feedback_type == CONTACT_REQUEST_FEEDBACK
        and (t := parse_time(f.created_at)) is not None and t >= cutoff
    ]
    if contact_requests:
        latest = max(contact_requests, key=lambda f: parse_time(f.created_at))
        detected.append(_result(
            "R5_USER_REQUESTS_FAMILY_CONTACT",
            "本人明确选择'希望家人联系我'。这是主动请求而非系统推断，"
            "应在授权范围内通知家属并生成待处理关怀事件。",
            {
                "feedback_type": latest.feedback_type,
                "created_at": iso_utc(parse_time(latest.created_at)),
                "share_with_family": latest.share_with_family,
            },
            "user_feedback",
            1.0,
            as_of_iso,
            severity="urgent",
        ))

    return {"detected": detected, "suppressed": suppressed}
