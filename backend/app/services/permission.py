"""授权校验：所有家属访问本人数据的唯一安全入口。

规则：
1. 只有 status=active 的 family_links 才有效。
2. 撤销授权后（status=revoked）立即拒绝。
3. permission_scope 是 JSON 数组字符串，为空表示未授权任何数据。
4. sos（一键呼救）事件由本人发起，不需要家属授权即可通知家属。
"""

import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.family import FamilyLink

ALL_SCOPES = {"checkins", "activities", "health", "care_events", "feedback", "baseline"}


def get_active_link(db: Session, owner_id: int, family_id: int) -> FamilyLink | None:
    """查找 本人->家属 的有效绑定。"""
    return (
        db.query(FamilyLink)
        .filter(
            FamilyLink.owner_id == owner_id,
            FamilyLink.family_id == family_id,
            FamilyLink.status == "active",
        )
        .first()
    )


def require_scope(db: Session, owner_id: int, family_id: int, scope: str) -> None:
    """要求家属对本人指定数据类型有授权，否则 403。"""
    link = get_active_link(db, owner_id, family_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="未建立有效的家庭绑定或授权已撤销",
        )
    scopes = parse_scope(link.permission_scope)
    if scope not in scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"未获得 {scope} 类型的查看授权",
        )


def parse_scope(scope_json: str | None) -> list[str]:
    """解析 permission_scope，过滤掉非法值。"""
    try:
        values = json.loads(scope_json or "[]")
    except (ValueError, TypeError):
        return []
    if not isinstance(values, list):
        return []
    return list(dict.fromkeys(v for v in values if v in ALL_SCOPES))
