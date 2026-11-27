"""基线接口：查询和触发重新计算。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.baseline import BaselineProfile
from app.models.user import User
from app.schemas.baseline import BaselineOut
from app.schemas.care import CareEventOut
from app.services.baseline_service import recalculate_baseline, run_change_detection

router = APIRouter(prefix="/baselines", tags=["生活基线"])


@router.get("/me", response_model=BaselineOut | None)
def get_my_baseline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取本人基线。从未计算过返回 null。"""
    return (
        db.query(BaselineProfile).filter(BaselineProfile.user_id == current_user.id).first()
    )


@router.post("/me/recalculate", response_model=BaselineOut)
def recalculate(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """触发重新计算本人基线。"""
    return recalculate_baseline(db, current_user.id)


@router.post("/me/detect-changes", response_model=list[CareEventOut])
def detect_my_changes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """运行变化识别并保存关怀事件。

    数据不足时返回空数组；同一规则已有未关闭事件时不会重复创建。
    该接口供算法模块或演示流程显式触发，不会在每次查询时产生副作用。
    """
    return run_change_detection(db, current_user.id)
