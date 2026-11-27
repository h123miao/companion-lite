"""活动记录接口：增删改查（本人端）。家属端查询在 dashboard 模块按授权提供。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import parse_aware
from app.database import get_db
from app.models.activity import ActivityRecord
from app.models.user import User
from app.schemas.activity import (
    ACTIVITY_TYPES,
    DATA_SOURCES,
    SYNC_STATUSES,
    ActivityCreate,
    ActivityOut,
    ActivityUpdate,
)

router = APIRouter(prefix="/activities", tags=["活动记录"])


@router.post("", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.activity_type not in ACTIVITY_TYPES:
        raise HTTPException(status_code=400, detail="activity_type 取值不合法")
    if payload.data_source not in DATA_SOURCES:
        raise HTTPException(status_code=400, detail="data_source 取值不合法")
    if payload.sync_status not in SYNC_STATUSES:
        raise HTTPException(status_code=400, detail="sync_status 取值不合法")

    activity = ActivityRecord(
        user_id=current_user.id,
        activity_type=payload.activity_type,
        recorded_at=parse_aware(payload.recorded_at),
        note=payload.note,
        data_source=payload.data_source,
        sync_status=payload.sync_status,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("/me", response_model=list[ActivityOut])
def list_my_activities(
    activity_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ActivityRecord).filter(ActivityRecord.user_id == current_user.id)
    if activity_type:
        query = query.filter(ActivityRecord.activity_type == activity_type)
    return query.order_by(ActivityRecord.recorded_at.desc()).limit(limit).all()


@router.put("/{activity_id}", response_model=ActivityOut)
def update_activity(
    activity_id: int,
    payload: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = db.query(ActivityRecord).filter(ActivityRecord.id == activity_id).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="活动记录不存在")
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的活动记录")

    if payload.activity_type is not None:
        if payload.activity_type not in ACTIVITY_TYPES:
            raise HTTPException(status_code=400, detail="activity_type 取值不合法")
        activity.activity_type = payload.activity_type
    if payload.recorded_at is not None:
        activity.recorded_at = parse_aware(payload.recorded_at)
    if payload.note is not None:
        activity.note = payload.note

    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = db.query(ActivityRecord).filter(ActivityRecord.id == activity_id).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="活动记录不存在")
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的活动记录")

    db.delete(activity)
    db.commit()
