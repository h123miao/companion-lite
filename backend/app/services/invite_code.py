"""邀请码生成与存储。

简化版：用内存字典存 邀请码 -> (owner_id, 过期时间)。
比赛 Demo 够用；正式部署时应改用数据库表或 Redis。
"""

import secrets
import string
from datetime import datetime, timedelta, timezone

from app.core.time_utils import utcnow

_code_store: dict[str, tuple[int, datetime]] = {}
CODE_VALID_MINUTES = 60
ALPHABET = string.ascii_uppercase + string.digits


def generate_invite_code(owner_id: int) -> str:
    """为本人的一次绑定申请生成 6 位邀请码，1 小时有效。"""
    code = "".join(secrets.choice(ALPHABET) for _ in range(6))
    _code_store[code] = (owner_id, utcnow() + timedelta(minutes=CODE_VALID_MINUTES))
    return code


def resolve_invite_code(code: str) -> int | None:
    """校验邀请码，有效返回 owner_id，无效或过期返回 None。"""
    entry = _code_store.get(code.upper())
    if entry is None:
        return None
    owner_id, expires_at = entry
    if utcnow() > expires_at:
        _code_store.pop(code.upper(), None)
        return None
    return owner_id


def consume_invite_code(code: str) -> None:
    """绑定成功后作废旧邀请码，防止重复使用。"""
    _code_store.pop(code.upper(), None)
