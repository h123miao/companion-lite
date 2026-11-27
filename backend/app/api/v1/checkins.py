"""签到接口：提交签到、查询本人历史。

第一个模块只实现本人端接口。
家属端查询需要 family_links 表和授权校验，等家庭模块开发时再加入。
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import parse_aware, utcnow
from app.database import get_db
from app.models.checkin import DailyCheckin
from app.models.user import User
from app.schemas.checkin import (
    DATA_SOURCES,
    MOOD_VALUES,
    STATUS_VALUES,
    SYNC_STATUSES,
    CheckinCreate,
    CheckinOut,
)

router = APIRouter(prefix="/checkins", tags=["签到"])


@router.post("", response_model=CheckinOut, status_code=status.HTTP_201_CREATED)
def create_checkin(
    payload: CheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交一条签到记录。时间统一转成 UTC 后存入数据库。"""
    if payload.mood is not None and payload.mood not in MOOD_VALUES:
        raise HTTPException(status_code=400, detail="mood 取值不合法")
    if payload.status not in STATUS_VALUES:
        raise HTTPException(status_code=400, detail="status 取值不合法")
    if payload.data_source not in DATA_SOURCES:
        raise HTTPException(status_code=400, detail="data_source 取值不合法")
    if payload.sync_status not in SYNC_STATUSES:
        raise HTTPException(status_code=400, detail="sync_status 取值不合法")

    checkin = DailyCheckin(
        user_id=current_user.id,
        check_in_at=parse_aware(payload.check_in_at),
        mood=payload.mood,
        status=payload.status,
        note=payload.note,
        data_source=payload.data_source,
        sync_status=payload.sync_status,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/me/today", response_model=list[CheckinOut])
def read_today_checkins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取本人最近 24 小时的签到记录。"""
    since = utcnow() - timedelta(hours=24)
    return (
        db.query(DailyCheckin)
        .filter(DailyCheckin.user_id == current_user.id, DailyCheckin.check_in_at >= since)
        .order_by(DailyCheckin.check_in_at.desc())
        .all()
    )


@router.get("/me", response_model=list[CheckinOut])
def read_my_checkins(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取本人签到历史，按时间倒序，最多 limit 条。"""
    return (
        db.query(DailyCheckin)
        .filter(DailyCheckin.user_id == current_user.id)
        .order_by(DailyCheckin.check_in_at.desc())
        .limit(limit)
        .all()
    )
