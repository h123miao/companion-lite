"""穿戴数据接口。

心率数据只记录与展示趋势，不做报警、不做医疗判断。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import parse_aware
from app.database import get_db
from app.models.device import DeviceBinding
from app.models.health import HealthRecord
from app.models.user import User
from app.schemas.device import (
    DATA_SOURCES,
    DATA_TYPES,
    HEALTH_UNITS,
    SYNC_STATUSES,
    HealthRecordCreate,
    HealthRecordOut,
)

router = APIRouter(prefix="/health-records", tags=["穿戴数据"])


@router.post("", response_model=HealthRecordOut, status_code=201)
def create_health_record(
    payload: HealthRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.data_type not in DATA_TYPES:
        raise HTTPException(status_code=400, detail="data_type 取值不合法")
    if payload.data_source not in DATA_SOURCES:
        raise HTTPException(status_code=400, detail="data_source 取值不合法")
    if payload.sync_status not in SYNC_STATUSES:
        raise HTTPException(status_code=400, detail="sync_status 取值不合法")

    if payload.device_binding_id is not None:
        device = db.query(DeviceBinding).filter(DeviceBinding.id == payload.device_binding_id).first()
        if (
            device is None
            or device.user_id != current_user.id
            or device.status == "unbound"
        ):
            raise HTTPException(status_code=400, detail="设备绑定不存在或不属于当前用户")

    collected_at = parse_aware(payload.collected_at)
    uploaded_at = parse_aware(payload.uploaded_at) if payload.uploaded_at else None
    if uploaded_at is not None and uploaded_at < collected_at:
        raise HTTPException(status_code=400, detail="uploaded_at 不能早于 collected_at")

    record = HealthRecord(
        user_id=current_user.id,
        device_binding_id=payload.device_binding_id,
        data_type=payload.data_type,
        value=payload.value,
        unit=HEALTH_UNITS[payload.data_type],
        collected_at=collected_at,
        uploaded_at=uploaded_at,
        data_source=payload.data_source,
        sync_status=payload.sync_status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/me", response_model=list[HealthRecordOut])
def list_health_records(
    data_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id)
    if data_type:
        query = query.filter(HealthRecord.data_type == data_type)
    return query.order_by(HealthRecord.collected_at.desc()).limit(limit).all()
