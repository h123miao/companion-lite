"""家庭关系接口：邀请码、绑定、确认、授权、解绑。"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import utcnow
from app.database import get_db
from app.models.family import FamilyLink
from app.models.user import User
from app.schemas.family import (
    FamilyBindIn,
    FamilyLinkOut,
    InviteCodeOut,
    PermissionUpdate,
    VALID_SCOPES,
)
from app.services import invite_code
from app.services.permission import parse_scope

router = APIRouter(prefix="/family", tags=["家庭关系"])


@router.post("/invite-code", response_model=InviteCodeOut)
def create_invite_code(current_user: User = Depends(get_current_user)):
    """本人生成邀请码，发给家属用于申请绑定。"""
    if current_user.role != "self":
        raise HTTPException(status_code=403, detail="只有本人账号可以生成邀请码")
    code = invite_code.generate_invite_code(current_user.id)
    return InviteCodeOut(invite_code=code)


@router.post("/bind", response_model=FamilyLinkOut, status_code=status.HTTP_201_CREATED)
def bind_family(
    payload: FamilyBindIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """家属用邀请码申请绑定，状态为 pending，等本人确认。"""
    if current_user.role != "family":
        raise HTTPException(status_code=403, detail="只有家属账号可以申请绑定")

    owner_id = invite_code.resolve_invite_code(payload.invite_code)
    if owner_id is None:
        raise HTTPException(status_code=400, detail="邀请码无效或已过期")
    if owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能绑定自己")

    existing = (
        db.query(FamilyLink)
        .filter(FamilyLink.owner_id == owner_id, FamilyLink.family_id == current_user.id)
        .first()
    )
    if existing:
        if existing.status == "revoked":
            # 允许重新申请：改为 pending
            existing.status = "pending"
            existing.confirmed_at = None
            existing.revoked_at = None
            existing.permission_scope = None
            existing.relation = payload.relation
            db.commit()
            db.refresh(existing)
            invite_code.consume_invite_code(payload.invite_code)
            return existing
        raise HTTPException(status_code=409, detail="已存在家庭绑定关系")

    link = FamilyLink(
        owner_id=owner_id,
        family_id=current_user.id,
        invite_code=payload.invite_code,
        relation=payload.relation,
        status="pending",
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    invite_code.consume_invite_code(payload.invite_code)
    return link


@router.get("/links", response_model=list[FamilyLinkOut])
def list_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看与我相关的家庭关系（本人或家属视角）。"""
    return (
        db.query(FamilyLink)
        .filter(
            (FamilyLink.owner_id == current_user.id) | (FamilyLink.family_id == current_user.id)
        )
        .order_by(FamilyLink.created_at.desc())
        .all()
    )


@router.put("/links/{link_id}/confirm", response_model=FamilyLinkOut)
def confirm_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """本人确认绑定。确认后状态为 active，但授权范围默认为空，需单独设置。"""
    link = db.query(FamilyLink).filter(FamilyLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="绑定记录不存在")
    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有本人可以确认绑定")
    if link.status != "pending":
        raise HTTPException(status_code=400, detail="该绑定不是待确认状态")

    link.status = "active"
    link.confirmed_at = utcnow()
    db.commit()
    db.refresh(link)
    return link


@router.put("/links/{link_id}/permission", response_model=FamilyLinkOut)
def update_permission(
    link_id: int,
    payload: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """本人设置家属可查看的数据类型和是否接收关怀提醒。"""
    link = db.query(FamilyLink).filter(FamilyLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="绑定记录不存在")
    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有本人可以设置授权")
    if link.status != "active":
        raise HTTPException(status_code=400, detail="绑定尚未生效")

    invalid = set(payload.permission_scope) - VALID_SCOPES
    if invalid:
        raise HTTPException(status_code=400, detail=f"非法授权类型: {sorted(invalid)}")

    scopes = list(dict.fromkeys(parse_scope(json.dumps(payload.permission_scope))))
    link.permission_scope = json.dumps(scopes)
    link.can_receive_alert = payload.can_receive_alert
    db.commit()
    db.refresh(link)
    return link


@router.delete("/links/{link_id}", response_model=FamilyLinkOut)
def revoke_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """本人撤销授权。撤销后立即阻止后续未授权访问。"""
    link = db.query(FamilyLink).filter(FamilyLink.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="绑定记录不存在")
    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有本人可以解除绑定")

    link.status = "revoked"
    link.revoked_at = utcnow()
    link.permission_scope = None
    link.can_receive_alert = False
    db.commit()
    db.refresh(link)
    return link
