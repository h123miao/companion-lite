"""核心算法一：个人生活基线（Personal Baseline）。

思路：不用统一阈值判断所有人，而是先用每个人自己过去 14 天的记录
算出"他/她自己的生活规律"。样本不足时明确输出"数据不足"，不做判断。

使用的统计量：中位数、均值、标准差、四分位距（IQR）、时间窗口。
这些都能在答辩时逐条解释，不需要深度学习模型。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from .rules import DEFAULT_CONFIG
from .schema import AnalysisInput
from .utils import (
    format_minutes,
    iso_utc,
    local_day,
    mean_or_none,
    minutes_of_day,
    normalize_minutes,
    parse_time,
    percentile,
    stdev_or_none,
)


@dataclass
class BaselineResult:
    sufficient: bool
    window_days: int
    coverage_days: int
    valid_checkins: int
    checkin_median_min: float | None = None
    checkin_mean_min: float | None = None
    checkin_std_min: float | None = None
    checkin_q1_min: float | None = None
    checkin_q3_min: float | None = None
    checkin_window_start: float | None = None
    checkin_window_end: float | None = None
    daily_activity_mean: float | None = None
    daily_activity_median: float | None = None
    active_days_per_week: float | None = None
    feedback_distribution: dict = field(default_factory=dict)
    insufficient_reason: str | None = None

    def to_dict(self) -> dict:
        """输出给后端 / Android 展示的 JSON 结构。"""
        return {
            "sufficient": self.sufficient,
            "window_days": self.window_days,
            "coverage_days": self.coverage_days,
            "valid_checkins": self.valid_checkins,
            "checkin_time_median": format_minutes(self.checkin_median_min),
            "checkin_time_mean": format_minutes(self.checkin_mean_min),
            "checkin_time_std_minutes": self.checkin_std_min,
            "checkin_time_iqr_minutes": (
                round(self.checkin_q3_min - self.checkin_q1_min, 2)
                if self.checkin_q1_min is not None and self.checkin_q3_min is not None
                else None
            ),
            "typical_checkin_window": {
                "start": format_minutes(self.checkin_window_start),
                "end": format_minutes(self.checkin_window_end),
            },
            "daily_activity_mean": self.daily_activity_mean,
            "daily_activity_median": self.daily_activity_median,
            "active_days_per_week": self.active_days_per_week,
            "feedback_distribution": self.feedback_distribution,
            "insufficient_reason": self.insufficient_reason,
        }


def compute_baseline(inp: AnalysisInput, config: dict | None = None) -> BaselineResult:
    """根据本人历史记录计算生活基线。"""
    cfg = {**DEFAULT_CONFIG, **(config or inp.config or {})}
    window_days = int(cfg["baseline_window_days"])
    min_days = int(cfg["baseline_min_days"])
    offset = float(cfg["timezone_offset_hours"])

    as_of = parse_time(inp.as_of)
    if as_of is None:
        return BaselineResult(
            sufficient=False,
            window_days=window_days,
            coverage_days=0,
            valid_checkins=0,
            insufficient_reason="分析基准时间无效，暂不判断",
        )

    cutoff = as_of - timedelta(days=window_days)

    # ---- 签到时间规律 ----
    recent_checkins = [
        c for c in inp.checkins
        if (t := parse_time(c.check_in_at)) is not None and cutoff <= t <= as_of
    ]
    checkin_days = {local_day(parse_time(c.check_in_at), offset) for c in recent_checkins}
    minutes = [normalize_minutes(minutes_of_day(parse_time(c.check_in_at), offset))
               for c in recent_checkins]

    # ---- 活动记录规律 ----
    activities = [
        a for a in inp.activities
        if (t := parse_time(a.recorded_at)) is not None and cutoff <= t <= as_of
    ]
    activity_days = {local_day(parse_time(a.recorded_at), offset) for a in activities}
    daily_counts: dict = {}
    for a in activities:
        day = local_day(parse_time(a.recorded_at), offset)
        daily_counts[day] = daily_counts.get(day, 0) + 1
    count_values = list(daily_counts.values())

    # ---- 主动反馈分布 ----
    feedbacks = [
        f for f in inp.feedbacks
        if (t := parse_time(f.created_at)) is not None and cutoff <= t <= as_of
    ]
    distribution: dict[str, int] = {}
    for f in feedbacks:
        distribution[f.feedback_type] = distribution.get(f.feedback_type, 0) + 1

    coverage_days = len(checkin_days)
    sufficient = coverage_days >= min_days and bool(minutes)

    if not sufficient:
        return BaselineResult(
            sufficient=False,
            window_days=window_days,
            coverage_days=coverage_days,
            valid_checkins=len(recent_checkins),
            daily_activity_mean=mean_or_none(count_values),
            daily_activity_median=percentile(count_values, 0.5),
            active_days_per_week=(
                round(len(activity_days) / max(coverage_days, 1) * 7, 2) if activity_days else 0.0
            ),
            feedback_distribution=distribution,
            insufficient_reason=(
                f"数据不足：最近 {window_days} 天只有 {coverage_days} 天签到记录，"
                f"至少需要 {min_days} 天，暂不判断生活规律"
            ),
        )

    q1 = percentile(minutes, 0.25)
    q3 = percentile(minutes, 0.75)
    iqr = (q3 - q1) if (q1 is not None and q3 is not None) else 0.0
    scale = float(cfg["checkin_window_iqr_scale"])
    min_width = float(cfg["checkin_min_window_minutes"])
    start = q1 - scale * iqr
    end = q3 + scale * iqr
    if end - start < min_width:
        center = (start + end) / 2
        start, end = center - min_width / 2, center + min_width / 2

    return BaselineResult(
        sufficient=True,
        window_days=window_days,
        coverage_days=coverage_days,
        valid_checkins=len(recent_checkins),
        checkin_median_min=percentile(minutes, 0.5),
        checkin_mean_min=mean_or_none(minutes),
        checkin_std_min=stdev_or_none(minutes),
        checkin_q1_min=q1,
        checkin_q3_min=q3,
        checkin_window_start=round(start, 2),
        checkin_window_end=round(end, 2),
        daily_activity_mean=mean_or_none(count_values),
        daily_activity_median=percentile(count_values, 0.5),
        active_days_per_week=(
            round(len(activity_days) / max(coverage_days, 1) * 7, 2) if activity_days else 0.0
        ),
        feedback_distribution=distribution,
        insufficient_reason=None,
    )
