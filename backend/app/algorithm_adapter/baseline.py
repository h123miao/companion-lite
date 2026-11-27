"""基线与变化识别算法（参考实现）。

这是成员 C 提供的临时参考实现，用 Python 标准库 statistics 完成，
只为让后端闭环能跑通。成员 D 完成正式算法（NumPy/Pandas）后替换本文件即可，
输入输出格式保持不变。
"""

import json
from datetime import datetime, time, timedelta

from app.core.time_utils import to_user_local, utcnow

MIN_VALID_DAYS = 7  # 少于 7 天有效数据，判定为数据不足


def _seconds_of_day(dt: datetime) -> int:
    return dt.hour * 3600 + dt.minute * 60 + dt.second


def _seconds_to_time(seconds: float) -> time:
    seconds = int(seconds) % 86400
    return time(hour=seconds // 3600, minute=(seconds % 3600) // 60, second=seconds % 60)


def _percentile(sorted_values: list[float], p: float) -> float:
    """简单百分位计算。"""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    index = p * (len(sorted_values) - 1)
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    frac = index - lower
    return sorted_values[lower] * (1 - frac) + sorted_values[upper] * frac


def compute_baseline(
    checkins: list[dict],
    activities: list[dict],
    feedbacks: list[dict],
    health_records: list[dict],
    window_days: int = 14,
    timezone_name: str = "UTC",
) -> dict:
    """计算个人生活基线。

    输入：各数据源的记录字典列表
    输出：基线字典（字段与 baseline_profiles 表对应）
    """
    cutoff = utcnow() - timedelta(days=window_days)

    recent_checkins = [
        c
        for c in checkins
        if c["check_in_at"] >= cutoff
        and c.get("sync_status", "synced") == "synced"
    ]
    local_checkins = [
        (c, to_user_local(c["check_in_at"], timezone_name)) for c in recent_checkins
    ]
    checkin_seconds = sorted(_seconds_of_day(local_time) for _, local_time in local_checkins)

    # 有效天数使用用户本地日期。数据库保存 UTC，但“每天几点签到”是本地生活规律。
    checkin_dates = {local_time.date() for _, local_time in local_checkins}
    valid_days = len(checkin_dates)
    data_sufficient = valid_days >= MIN_VALID_DAYS and len(checkin_seconds) >= MIN_VALID_DAYS

    baseline = {
        "window_days": window_days,
        "valid_days": valid_days,
        "data_sufficient": data_sufficient,
        "checkin_time_median": None,
        "checkin_time_mean": None,
        "checkin_time_stddev": 0.0,
        "checkin_iqr_min": None,
        "checkin_iqr_max": None,
        "avg_daily_activities": 0.0,
        "avg_weekly_activities": 0.0,
        "avg_daily_steps": 0.0,
        "feedback_distribution": json.dumps({}),
    }

    if checkin_seconds:
        n = len(checkin_seconds)
        mean = sum(checkin_seconds) / n
        median = _percentile(checkin_seconds, 0.5)
        variance = sum((x - mean) ** 2 for x in checkin_seconds) / n
        q1 = _percentile(checkin_seconds, 0.25)
        q3 = _percentile(checkin_seconds, 0.75)
        baseline["checkin_time_median"] = _seconds_to_time(median)
        baseline["checkin_time_mean"] = _seconds_to_time(mean)
        baseline["checkin_time_stddev"] = round(variance ** 0.5, 2)
        baseline["checkin_iqr_min"] = _seconds_to_time(q1)
        baseline["checkin_iqr_max"] = _seconds_to_time(q3)

    recent_activities = [
        a
        for a in activities
        if a["recorded_at"] >= cutoff and a.get("sync_status", "synced") == "synced"
    ]
    activity_dates = [
        to_user_local(a["recorded_at"], timezone_name).date() for a in recent_activities
    ]
    covered_activity_count = sum(date in checkin_dates for date in activity_dates)
    if valid_days:
        # 只除以“有有效签到覆盖的本地天数”，避免把未知数据当成零活动。
        avg_daily = covered_activity_count / valid_days
        baseline["avg_daily_activities"] = round(avg_daily, 2)
        baseline["avg_weekly_activities"] = round(avg_daily * 7, 2)

    daily_steps: dict = {}
    for record in health_records:
        if (
            record["data_type"] != "steps"
            or record["collected_at"] < cutoff
            or record.get("sync_status", "synced") != "synced"
            or not record.get("is_valid", True)
        ):
            continue
        local_date = to_user_local(record["collected_at"], timezone_name).date()
        # 穿戴设备常上报当天累计步数；同一天取最大值，避免把累计值相加。
        daily_steps[local_date] = max(daily_steps.get(local_date, 0.0), record["value"])
    if daily_steps:
        baseline["avg_daily_steps"] = round(sum(daily_steps.values()) / len(daily_steps), 2)

    distribution: dict[str, int] = {}
    for f in feedbacks:
        if f["created_at"] < cutoff:
            continue
        distribution[f["feedback_type"]] = distribution.get(f["feedback_type"], 0) + 1
    baseline["feedback_distribution"] = json.dumps(distribution)

    return baseline


def detect_changes(
    baseline: dict,
    checkins: list[dict],
    feedbacks: list[dict],
    timezone_name: str = "UTC",
) -> list[dict]:
    """变化识别（规则一：签到时间偏离；规则三：反馈变化）。

    重要：数据不足时不产出任何变化结论。
    """
    if not baseline.get("data_sufficient"):
        return []

    changes = []

    # 规则一：最近一次签到是否晚于 IQR 上界 1 小时以上
    iqr_max = baseline.get("checkin_iqr_max")
    if iqr_max and checkins:
        latest = max(checkins, key=lambda c: c["check_in_at"])
        latest_seconds = _seconds_of_day(
            to_user_local(latest["check_in_at"], timezone_name)
        )
        iqr_max_seconds = iqr_max.hour * 3600 + iqr_max.minute * 60
        if latest_seconds > iqr_max_seconds + 3600:
            changes.append({
                "event_type": "checkin_delay",
                "trigger_rule": "rule_checkin_time_deviation",
                "concern_level": "low",
                "reason": f"最近签到时间明显晚于本人历史规律（历史区间上限 {iqr_max.strftime('%H:%M')}）",
                "evidence": json.dumps({"iqr_max": iqr_max.strftime("%H:%M")}),
            })

    # 规则三：最近 3 次反馈连续为 unwell 或 need_help
    recent_feedback = sorted(feedbacks, key=lambda f: f["created_at"], reverse=True)[:3]
    if len(recent_feedback) == 3 and all(
        f["feedback_type"] in {"unwell", "need_help"} for f in recent_feedback
    ):
        changes.append({
            "event_type": "feedback_concern",
            "trigger_rule": "rule_feedback_consecutive",
            "concern_level": "medium",
            "reason": "最近 3 次反馈连续表示状态不佳",
            "evidence": json.dumps({"feedback_types": [f["feedback_type"] for f in recent_feedback]}),
        })

    return changes
