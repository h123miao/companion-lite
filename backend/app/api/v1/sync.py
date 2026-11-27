"""数据同步日志接口。用于区分离线、同步延迟和数据缺失。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import parse_aware
from app.database import get_db
from app.models.device import DeviceBinding
from app.models.sync import DataSyncLog
from app.models.user import User
from app.schemas.device import SYNC_LOG_STATUSES, SyncLogCreate, SyncLogOut

router = APIRouter(prefix="/sync-logs", tags=["同步日志"])


@router.post("", response_model=SyncLogOut, status_code=201)
def create_sync_log(
    payload: SyncLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in SYNC_LOG_STATUSES:
        raise HTTPException(status_code=400, detail="status 取值不合法")

    if payload.device_binding_id is not None:
        device = (
            db.query(DeviceBinding)
            .filter(DeviceBinding.id == payload.device_binding_id)
            .first()
        )
        if (
            device is None
            or device.user_id != current_user.id
            or device.status == "unbound"
        ):
            raise HTTPException(status_code=400, detail="设备绑定不存在或不属于当前用户")

    started_at = parse_aware(payload.started_at)
    finished_at = parse_aware(payload.finished_at) if payload.finished_at else None
    if finished_at is not None and finished_at < started_at:
        raise HTTPException(status_code=400, detail="finished_at 不能早于 started_at")

    log = DataSyncLog(
        user_id=current_user.id,
        device_binding_id=payload.device_binding_id,
        sync_type=payload.sync_type,
        status=payload.status,
        started_at=started_at,
        finished_at=finished_at,
        records_count=payload.records_count,
        error_message=payload.error_message,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/me", response_model=list[SyncLogOut])
def list_sync_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(DataSyncLog)
        .filter(DataSyncLog.user_id == current_user.id)
        .order_by(DataSyncLog.started_at.desc())
        .limit(100)
        .all()
    )
