"""关怀事件接口：完整闭环。

本人端：查看询问、回应、通知家属、一键呼救。
家属端：查看待处理事件、标记已联系、关闭事件（需授权）。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time_utils import utcnow
from app.database import get_db
from app.models.care import CareEvent
from app.models.family import FamilyLink
from app.models.feedback import UserFeedback
from app.models.user import User
from app.schemas.care import (
    CONCERN_LEVELS,
    EVENT_TYPES,
    USER_RESPONSES,
    CareEventCreate,
    CareEventOut,
    RespondIn,
)
from app.services.permission import parse_scope

router = APIRouter(prefix="/care-events", tags=["关怀事件"])


def _get_targeted_family_link(
    db: Session,
    event: CareEvent,
    family_id: int,
) -> FamilyLink:
    """确认事件确实通知给了当前家属，且该家属仍有 care_events 授权。"""
    if event.family_notified_at is None or event.family_link_id is None:
        raise HTTPException(status_code=403, detail="该事件未获授权查看")
    link = (
        db.query(FamilyLink)
        .filter(
            FamilyLink.id == event.family_link_id,
            FamilyLink.family_id == family_id,
            FamilyLink.status == "active",
        )
        .first()
    )
    if link is None or "care_events" not in parse_scope(link.permission_scope):
        raise HTTPException(status_code=403, detail="该事件未获授权查看")
    return link


@router.post("", response_model=CareEventOut, status_code=201)
def create_care_event(
    payload: CareEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建关怀事件（通常由算法触发，本人也可主动创建）。"""
    if payload.event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail="event_type 取值不合法")
    if payload.concern_level not in CONCERN_LEVELS:
        raise HTTPException(status_code=400, detail="concern_level 取值不合法")

    event = CareEvent(
        user_id=current_user.id,
        event_type=payload.event_type,
        trigger_rule=payload.trigger_rule,
        concern_level=payload.concern_level,
        reason=payload.reason,
        evidence=payload.evidence,
        event_status="pending",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/me", response_model=list[CareEventOut])
def my_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """本人收到的关怀询问。"""
    return (
        db.query(CareEvent)
        .filter(CareEvent.user_id == current_user.id)
        .order_by(CareEvent.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/family", response_model=list[CareEventOut])
def family_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """家属待处理事件：只返回已授权本人、且已通知家属的事件。"""
    links = (
        db.query(FamilyLink)
        .filter(FamilyLink.family_id == current_user.id, FamilyLink.status == "active")
        .all()
    )
    link_ids = []
    for link in links:
        scopes = parse_scope(link.permission_scope)
        if "care_events" in scopes:
            link_ids.append(link.id)
    if not link_ids:
        return []

    return (
        db.query(CareEvent)
        .filter(
            CareEvent.family_link_id.in_(link_ids),
            CareEvent.family_notified_at.isnot(None),
        )
        .order_by(CareEvent.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/{event_id}", response_model=CareEventOut)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(CareEvent).filter(CareEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")

    if event.user_id == current_user.id:
        return event
    _get_targeted_family_link(db, event, current_user.id)
    return event


@router.post("/{event_id}/ask", response_model=CareEventOut)
def ask_user(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记为已向本人发出询问。"""
    event = db.query(CareEvent).filter(CareEvent.id == event_id).first()
    if event is None or event.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="事件不存在")
    if event.event_status in {"answered", "family_pending", "closed"}:
        raise HTTPException(status_code=409, detail="当前事件状态不能再次发起询问")
    event.event_status = "asking"
    event.asked_at = utcnow()
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/respond", response_model=CareEventOut)
def respond(
    event_id: int,
    payload: RespondIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """本人回应关怀询问，同时保存一条 user_feedback。"""
    if payload.response not in USER_RESPONSES:
        raise HTTPException(status_code=400, detail="response 取值不合法")

    event = db.query(CareEvent).filter(CareEvent.id == event_id).first()
    if event is None or event.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="事件不存在")
    if event.event_status not in {"pending", "asking"}:
        raise HTTPException(status_code=409, detail="当前事件状态不能提交回应")

    event.user_response = payload.response
    event.responded_at = utcnow()
    event.event_status = "answered"

    feedback = UserFeedback(
        user_id=current_user.id,
        care_event_id=event.id,
        feedback_type=payload.response,
        source="care_response",
    )
    db.add(feedback)
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/notify-family", response_model=CareEventOut)
def notify_family(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """按授权通知家属。没有授权家属时返回 400。"""
    event = db.query(CareEvent).filter(CareEvent.id == event_id).first()
    if event is None or event.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="事件不存在")
    if event.event_status == "closed":
        raise HTTPException(status_code=409, detail="事件已经关闭")
    if event.family_notified_at is not None:
        # 重复调用不改变已经选定的家属，避免一次事件被转发给另一位家属。
        return event

    links = (
        db.query(FamilyLink)
        .filter(FamilyLink.owner_id == current_user.id, FamilyLink.status == "active")
        .all()
    )
    authorized = [
        l for l in links
        if "care_events" in parse_scope(l.permission_scope) and l.can_receive_alert
    ]
    if not authorized:
        raise HTTPException(
            status_code=400,
            detail="没有同时获得关怀事件授权并开启提醒的家属",
        )

    target = authorized[0]
    event.family_link_id = target.id
    event.family_notified_at = utcnow()
    event.event_status = "family_pending"
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/mark-contacted", response_model=CareEventOut)
def mark_contacted(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """家属标记已联系本人（需授权）。"""
    event = db.query(CareEvent).filter(CareEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    _get_targeted_family_link(db, event, current_user.id)
    if event.event_status != "family_pending":
        raise HTTPException(status_code=409, detail="当前事件不在待家属处理状态")

    event.family_contacted_at = utcnow()
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/close", response_model=CareEventOut)
def close_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """关闭事件。本人或已授权家属可操作。"""
    event = db.query(CareEvent).filter(CareEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    if event.user_id != current_user.id:
        _get_targeted_family_link(db, event, current_user.id)
    if event.event_status == "closed":
        raise HTTPException(status_code=409, detail="事件已经关闭")

    event.event_status = "closed"
    event.handled_at = utcnow()
    db.commit()
    db.refresh(event)
    return event


@router.post("/sos", response_model=CareEventOut, status_code=201)
def sos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """一键呼救：本人主动触发，创建紧急事件并通知已授权家属。

    系统不自动拨打 120。由用户本人或家属拨打电话。
    """
    links = (
        db.query(FamilyLink)
        .filter(FamilyLink.owner_id == current_user.id, FamilyLink.status == "active")
        .all()
    )
    authorized = [
        l for l in links
        if "care_events" in parse_scope(l.permission_scope) and l.can_receive_alert
    ]

    event = CareEvent(
        user_id=current_user.id,
        event_type="sos",
        is_emergency=True,
        trigger_rule="user_manual_sos",
        concern_level="high",
        reason="用户主动发起一键呼救",
        event_status="family_pending" if authorized else "pending",
        family_link_id=authorized[0].id if authorized else None,
        family_notified_at=utcnow() if authorized else None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
