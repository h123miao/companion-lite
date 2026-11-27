"""设备绑定接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import utcnow
from app.database import get_db
from app.models.device import DeviceBinding
from app.models.user import User
from app.schemas.device import DEVICE_TYPES, DeviceCreate, DeviceOut, DeviceStatusUpdate

router = APIRouter(prefix="/devices", tags=["设备"])


@router.post("", response_model=DeviceOut, status_code=201)
def bind_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.device_type not in DEVICE_TYPES:
        raise HTTPException(status_code=400, detail="device_type 取值不合法")

    existing = (
        db.query(DeviceBinding)
        .filter(DeviceBinding.user_id == current_user.id, DeviceBinding.device_id == payload.device_id)
        .first()
    )
    if existing:
        if existing.status == "unbound":
            existing.status = "active"
            existing.unbound_at = None
            existing.device_name = payload.device_name
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=409, detail="设备已绑定")

    device = DeviceBinding(
        user_id=current_user.id,
        device_type=payload.device_type,
        device_id=payload.device_id,
        device_name=payload.device_name,
        status="active",
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/me", response_model=list[DeviceOut])
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(DeviceBinding)
        .filter(DeviceBinding.user_id == current_user.id, DeviceBinding.status != "unbound")
        .order_by(DeviceBinding.bound_at.desc())
        .all()
    )


@router.put("/{device_id}/status", response_model=DeviceOut)
def update_device_status(
    device_id: int,
    payload: DeviceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in {"active", "offline", "unbound"}:
        raise HTTPException(status_code=400, detail="status 取值不合法")
    device = db.query(DeviceBinding).filter(DeviceBinding.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能操作自己的设备")

    device.status = payload.status
    if payload.status == "active":
        device.last_seen_at = utcnow()
    if payload.status == "unbound":
        device.unbound_at = utcnow()
    db.commit()
    db.refresh(device)
    return device


@router.delete("/{device_id}", status_code=204)
def unbind_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = db.query(DeviceBinding).filter(DeviceBinding.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在")
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能操作自己的设备")
    device.status = "unbound"
    device.unbound_at = utcnow()
    db.commit()
