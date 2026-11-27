"""时间是整个项目最容易出错的地方，统一在这里处理。

规则：数据库一律存 UTC 时间（无时区信息的 datetime，但语义是 UTC）。
展示时由客户端按 user.timezone 转换。
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def _resolve_timezone(value: str):
    """解析 IANA 时区；Windows 未安装 tzdata 时保留中国常用时区兜底。"""
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError:
        # Asia/Shanghai 自 1991 年后没有夏令时，固定 +08:00 与当前生活场景一致。
        fallback = {
            "UTC": timezone.utc,
            "Asia/Shanghai": timezone(timedelta(hours=8)),
            "Asia/Chongqing": timezone(timedelta(hours=8)),
            "Asia/Hong_Kong": timezone(timedelta(hours=8)),
        }
        if value in fallback:
            return fallback[value]
        raise


def utcnow() -> datetime:
    """返回当前的 UTC 时间（naive datetime，语义为 UTC）。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_aware(value: datetime) -> datetime:
    """把带时区的 datetime 转成 UTC naive datetime；不带时区时按 UTC 处理。"""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def validate_timezone_name(value: str) -> str:
    """校验 IANA 时区名称，例如 Asia/Shanghai。"""
    try:
        _resolve_timezone(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("timezone 必须是有效的 IANA 时区名称") from None
    return value


def to_user_local(value: datetime, timezone_name: str) -> datetime:
    """把数据库中的 UTC 时间转换为用户本地时间。

    数据库中的 datetime 不带时区，但项目约定它表示 UTC，因此先补上 UTC
    时区再转换。返回值保留时区信息，便于按用户本地日期分组。
    """
    utc_value = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    return utc_value.astimezone(_resolve_timezone(timezone_name))
