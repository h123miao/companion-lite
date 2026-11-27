"""看板接口：本人端首页与家属端首页。

家属端严格按 family_links.permission_scope 过滤，
未授权的数据一律不返回。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.activity import ActivityRecord
from app.models.baseline import BaselineProfile
from app.models.care import CareEvent
from app.models.checkin import DailyCheckin
from app.models.device import DeviceBinding
from app.models.family import FamilyLink
from app.models.feedback import UserFeedback
from app.models.sync import DataSyncLog
from app.models.user import User
from app.services.permission import parse_scope

router = APIRouter(prefix="/dashboard", tags=["看板"])


def _data_status(db: Session, user_id: int) -> dict:
    """数据可信度状态摘要：区分设备离线、同步延迟、数据不足。"""
    # 取所有未解绑设备；只要有 offline 的，状态就应反映为离线
    devices = (
        db.query(DeviceBinding)
        .filter(DeviceBinding.user_id == user_id, DeviceBinding.status != "unbound")
        .all()
    )
    device_status = "offline" if any(d.status == "offline" for d in devices) else (
        "active" if devices else "unbound"
    )
    last_sync = (
        db.query(DataSyncLog)
        .filter(DataSyncLog.user_id == user_id)
        .order_by(DataSyncLog.started_at.desc())
        .first()
    )
    baseline = db.query(BaselineProfile).filter(BaselineProfile.user_id == user_id).first()

    sync_status = last_sync.status if last_sync else "none"
    sufficient = baseline.data_sufficient if baseline else False

    if device_status == "offline":
        note = "设备离线，未收到的数据不代表没有活动"
    elif sync_status in {"pending", "failed"}:
        note = "数据同步延迟，部分数据尚未上传"
    elif not sufficient:
        note = "数据不足，暂不判断生活规律变化"
    else:
        note = "数据状态正常"

    return {
        "device_status": device_status,
        "last_sync_status": sync_status,
        "data_sufficient": sufficient,
        "note": note,
    }


@router.get("/self")
def self_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """本人端首页：签到、活动、基线、数据状态、关怀提醒。"""
    latest_checkins = (
        db.query(DailyCheckin)
        .filter(DailyCheckin.user_id == current_user.id)
        .order_by(DailyCheckin.check_in_at.desc())
        .limit(5)
        .all()
    )
    latest_activities = (
        db.query(ActivityRecord)
        .filter(ActivityRecord.user_id == current_user.id)
        .order_by(ActivityRecord.recorded_at.desc())
        .limit(5)
        .all()
    )
    pending_events = (
        db.query(CareEvent)
        .filter(CareEvent.user_id == current_user.id, CareEvent.event_status.in_(["pending", "asking"]))
        .order_by(CareEvent.created_at.desc())
        .all()
    )
    baseline = (
        db.query(BaselineProfile).filter(BaselineProfile.user_id == current_user.id).first()
    )

    return {
        "user_id": current_user.id,
        "recent_checkins": [
            {"check_in_at": c.check_in_at.isoformat(), "mood": c.mood, "status": c.status}
            for c in latest_checkins
        ],
        "recent_activities": [
            {"activity_type": a.activity_type, "recorded_at": a.recorded_at.isoformat()}
            for a in latest_activities
        ],
        "baseline": {
            "data_sufficient": baseline.data_sufficient if baseline else False,
            "checkin_time_median": baseline.checkin_time_median.isoformat() if baseline and baseline.checkin_time_median else None,
        },
        "pending_care_events": [
            {"id": e.id, "event_type": e.event_type, "reason": e.reason, "event_status": e.event_status}
            for e in pending_events
        ],
        "data_status": _data_status(db, current_user.id),
    }


@router.get("/family/{user_id}")
def family_dashboard(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """家属端首页：只返回本人明确授权的数据。"""
    link = (
        db.query(FamilyLink)
        .filter(
            FamilyLink.owner_id == user_id,
            FamilyLink.family_id == current_user.id,
            FamilyLink.status == "active",
        )
        .first()
    )
    if link is None:
        raise HTTPException(status_code=403, detail="未建立有效的家庭绑定")

    scopes = parse_scope(link.permission_scope)
    owner = db.query(User).filter(User.id == user_id).first()
    if owner is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    result: dict = {
        "user_id": user_id,
        "display_name": owner.display_name,
        "authorized_scopes": scopes,
    }

    if "checkins" in scopes:
        rows = (
            db.query(DailyCheckin)
            .filter(DailyCheckin.user_id == user_id)
            .order_by(DailyCheckin.check_in_at.desc())
            .limit(5)
            .all()
        )
        result["recent_checkins"] = [
            {"check_in_at": c.check_in_at.isoformat(), "mood": c.mood, "status": c.status}
            for c in rows
        ]

    if "activities" in scopes:
        rows = (
            db.query(ActivityRecord)
            .filter(ActivityRecord.user_id == user_id)
            .order_by(ActivityRecord.recorded_at.desc())
            .limit(5)
            .all()
        )
        result["recent_activities"] = [
            {"activity_type": a.activity_type, "recorded_at": a.recorded_at.isoformat()}
            for a in rows
        ]

    if "care_events" in scopes:
        rows = (
            db.query(CareEvent)
            .filter(
                CareEvent.user_id == user_id,
                CareEvent.family_link_id == link.id,
                CareEvent.family_notified_at.isnot(None),
            )
            .order_by(CareEvent.created_at.desc())
            .limit(10)
            .all()
        )
        result["care_events"] = [
            {
                "id": e.id,
                "event_type": e.event_type,
                "event_status": e.event_status,
                "reason": e.reason,
                "is_emergency": e.is_emergency,
            }
            for e in rows
        ]

    if "feedback" in scopes:
        rows = (
            db.query(UserFeedback)
            .filter(UserFeedback.user_id == user_id)
            .order_by(UserFeedback.created_at.desc())
            .limit(10)
            .all()
        )
        result["feedbacks"] = [
            {"feedback_type": f.feedback_type, "content": f.content, "created_at": f.created_at.isoformat()}
            for f in rows
        ]

    if "baseline" in scopes:
        baseline = db.query(BaselineProfile).filter(BaselineProfile.user_id == user_id).first()
        result["baseline"] = {
            "data_sufficient": baseline.data_sufficient if baseline else False,
            "checkin_time_median": baseline.checkin_time_median.isoformat() if baseline and baseline.checkin_time_median else None,
        }

    # 数据状态对家属可见（帮助理解"没有数据不代表危险"）
    result["data_status"] = _data_status(db, user_id)
    return result
