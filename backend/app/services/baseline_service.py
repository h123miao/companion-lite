"""基线计算服务：从数据库组装算法输入，调用算法，保存输出。"""

from sqlalchemy.orm import Session

from app.algorithm_adapter.baseline import compute_baseline, detect_changes
from app.models.activity import ActivityRecord
from app.models.baseline import BaselineProfile
from app.models.care import CareEvent
from app.models.checkin import DailyCheckin
from app.models.feedback import UserFeedback
from app.models.health import HealthRecord
from app.models.user import User


def recalculate_baseline(db: Session, user_id: int, window_days: int = 14) -> BaselineProfile:
    """重新计算指定用户的基线，并写入数据库。"""
    from datetime import timedelta

    from app.core.time_utils import utcnow

    cutoff = utcnow() - timedelta(days=window_days)

    checkins = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user_id, DailyCheckin.check_in_at >= cutoff
    ).all()
    activities = db.query(ActivityRecord).filter(
        ActivityRecord.user_id == user_id, ActivityRecord.recorded_at >= cutoff
    ).all()
    feedbacks = db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id, UserFeedback.created_at >= cutoff
    ).all()
    health = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id, HealthRecord.collected_at >= cutoff
    ).all()
    user = db.query(User).filter(User.id == user_id).first()
    timezone_name = user.timezone if user else "UTC"

    checkin_dicts = [
        {"check_in_at": c.check_in_at, "sync_status": c.sync_status} for c in checkins
    ]
    activity_dicts = [
        {
            "activity_type": a.activity_type,
            "recorded_at": a.recorded_at,
            "sync_status": a.sync_status,
        }
        for a in activities
    ]
    feedback_dicts = [
        {"feedback_type": f.feedback_type, "created_at": f.created_at} for f in feedbacks
    ]
    health_dicts = [
        {
            "data_type": h.data_type,
            "value": float(h.value),
            "collected_at": h.collected_at,
            "sync_status": h.sync_status,
            "is_valid": h.is_valid,
        }
        for h in health
    ]

    result = compute_baseline(
        checkin_dicts,
        activity_dicts,
        feedback_dicts,
        health_dicts,
        window_days,
        timezone_name,
    )

    profile = db.query(BaselineProfile).filter(BaselineProfile.user_id == user_id).first()
    if profile is None:
        profile = BaselineProfile(user_id=user_id)
        db.add(profile)

    for key, value in result.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


def run_change_detection(db: Session, user_id: int) -> list[CareEvent]:
    """基于当前基线运行变化识别，为每条变化创建关怀事件。

    数据不足时不创建任何事件。
    """
    from datetime import timedelta

    from app.core.time_utils import utcnow

    profile = db.query(BaselineProfile).filter(BaselineProfile.user_id == user_id).first()
    if profile is None or not profile.data_sufficient:
        return []

    cutoff = utcnow() - timedelta(days=profile.window_days)
    checkins = db.query(DailyCheckin).filter(
        DailyCheckin.user_id == user_id, DailyCheckin.check_in_at >= cutoff
    ).all()
    feedbacks = db.query(UserFeedback).filter(
        UserFeedback.user_id == user_id, UserFeedback.created_at >= cutoff
    ).all()
    user = db.query(User).filter(User.id == user_id).first()
    timezone_name = user.timezone if user else "UTC"

    baseline_dict = {
        "data_sufficient": profile.data_sufficient,
        "checkin_iqr_max": profile.checkin_iqr_max,
    }
    changes = detect_changes(
        baseline_dict,
        [{"check_in_at": c.check_in_at} for c in checkins],
        [{"feedback_type": f.feedback_type, "created_at": f.created_at} for f in feedbacks],
        timezone_name,
    )

    events = []
    for change in changes:
        duplicated = (
            db.query(CareEvent.id)
            .filter(
                CareEvent.user_id == user_id,
                CareEvent.trigger_rule == change["trigger_rule"],
                CareEvent.event_status != "closed",
            )
            .first()
        )
        if duplicated:
            continue
        event = CareEvent(
            user_id=user_id,
            event_type=change["event_type"],
            trigger_rule=change["trigger_rule"],
            concern_level=change["concern_level"],
            reason=change["reason"],
            evidence=change.get("evidence"),
            event_status="pending",
        )
        db.add(event)
        events.append(event)
    db.commit()
    for event in events:
        db.refresh(event)
    return events
