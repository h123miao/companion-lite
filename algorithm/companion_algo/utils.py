"""通用工具：时间解析、本地时区换算、统计辅助。

项目约定：所有时间字段统一保存为 ISO 8601 UTC 字符串，例如
"2026-11-26T08:30:00Z"。分析"生活规律"时需要按用户本地时间理解
签到时刻，默认按 UTC+8（北京时间）换算，可通过 config 修改。
"""

from __future__ import annotations

import math
import statistics
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable


def parse_time(value: Any) -> datetime | None:
    """把 ISO 8601 字符串解析为 UTC datetime；解析失败返回 None（不抛异常）。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_utc(dt: datetime | None) -> str | None:
    """把 datetime 输出为统一的 UTC 字符串，便于写库。"""
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_local(dt_utc: datetime, offset_hours: float = 8.0) -> datetime:
    return dt_utc.astimezone(timezone(timedelta(hours=offset_hours)))


def local_day(dt_utc: datetime, offset_hours: float = 8.0) -> date:
    return to_local(dt_utc, offset_hours).date()


def minutes_of_day(dt_utc: datetime, offset_hours: float = 8.0) -> int:
    """取本地时间的"当天分钟数"，例如 08:30 -> 510。"""
    local = to_local(dt_utc, offset_hours)
    return local.hour * 60 + local.minute


def normalize_minutes(minutes: int) -> int:
    """把凌晨 00:00—03:59 的记录当作"次日凌晨"处理。

    否则一个人常在 01:00 签到，另几次在 23:30 签到，直接求中位数会
    把两个相近的习惯算成相差 22 小时。这里统一加 1440 分钟。
    """
    return minutes + 1440 if minutes < 240 else minutes


def format_minutes(minutes: float | int | None) -> str | None:
    """把分钟数格式化为 HH:MM（跨日部分取模，只用于展示）。"""
    if minutes is None:
        return None
    value = int(round(minutes)) % 1440
    return f"{value // 60:02d}:{value % 60:02d}"


def percentile(values: Iterable[float], q: float) -> float | None:
    """线性插值分位数。q=0.25 为下四分位数，q=0.75 为上四分位数。"""
    data = sorted(float(v) for v in values)
    if not data:
        return None
    if len(data) == 1:
        return data[0]
    position = (len(data) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return data[lower]
    return data[lower] + (data[upper] - data[lower]) * (position - lower)


def mean_or_none(values: Iterable[float]) -> float | None:
    data = list(values)
    return round(statistics.mean(data), 2) if data else None


def stdev_or_none(values: Iterable[float]) -> float | None:
    data = list(values)
    return round(statistics.stdev(data), 2) if len(data) >= 2 else 0.0


def to_jsonable(value: Any) -> Any:
    """递归把 dataclass / Enum / datetime 转成可 JSON 序列化的对象。"""
    from dataclasses import asdict, is_dataclass
    from enum import Enum

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return iso_utc(value)
    if isinstance(value, date):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(v) for v in value]
    return value
