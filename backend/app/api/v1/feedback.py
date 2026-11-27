"""用户反馈接口：主动反馈提交与查询。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.feedback import UserFeedback
from app.models.user import User
from app.schemas.care import FEEDBACK_TYPES, FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/feedback", tags=["用户反馈"])


@router.post("", response_model=FeedbackOut, status_code=201)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.feedback_type not in FEEDBACK_TYPES:
        raise HTTPException(status_code=400, detail="feedback_type 取值不合法")

    if payload.care_event_id is not None:
        from app.models.care import CareEvent

        event = db.query(CareEvent).filter(CareEvent.id == payload.care_event_id).first()
        if event is None or event.user_id != current_user.id:
            raise HTTPException(status_code=400, detail="关怀事件不存在或不属于当前用户")

    feedback = UserFeedback(
        user_id=current_user.id,
        feedback_type=payload.feedback_type,
        content=payload.content,
        care_event_id=payload.care_event_id,
        source="manual",
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/me", response_model=list[FeedbackOut])
def my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(UserFeedback)
        .filter(UserFeedback.user_id == current_user.id)
        .order_by(UserFeedback.created_at.desc())
        .limit(100)
        .all()
    )
