"""核心算法四：主动关怀触发（Care Trigger）。

核心原则（不可妥协）：
1. 系统发现生活规律变化后，先问本人，不能直接对家属说"用户出事了"。
2. 数据缺失、设备离线、同步延迟都不是危险结论。
3. 只有本人明确反馈（身体不适或请求联系），且存在有效授权时，才通知家属。
4. 没有授权就不通知，即使发现了变化。
"""

from __future__ import annotations

from copy import deepcopy

from .baseline import BaselineResult
from .credibility import CredibilityReport
from .rules import CONTACT_REQUEST_FEEDBACK, DEFAULT_CONFIG, NEGATIVE_FEEDBACK_TYPES
from .schema import AnalysisInput
from .utils import iso_utc, parse_time

CARE_OPTIONS = [
    {"value": "feeling_good", "label": "我很好"},
    {"value": "busy_today", "label": "今天比较忙"},
    {"value": "feeling_unwell", "label": "今天不太舒服"},
    {"value": "want_family_contact", "label": "希望家人联系我"},
    {"value": "declined_to_answer", "label": "暂时不想回答"},
]


def _authorized_family_ids(inp: AnalysisInput) -> list[int]:
    """返回可以接收关怀提醒的家属 ID（后端仍必须二次校验授权）。"""
    return [
        a.family_user_id for a in inp.authorizations
        if a.status == "active"
        and a.can_receive_alerts
        and ("care_events" in a.scope or "status" in a.scope)
    ]


def build_care_event(
    inp: AnalysisInput,
    baseline: BaselineResult,
    credibility: CredibilityReport,
    changes: dict,
    config: dict | None = None,
) -> dict | None:
    """根据变化识别结果生成关怀事件；没有变化返回 None。"""
    cfg = {**DEFAULT_CONFIG, **(config or inp.config or {})}
    detected = changes.get("detected") or []
    if not detected:
        return None

    as_of_iso = iso_utc(parse_time(inp.as_of))
    rule_ids = [d["rule_id"] for d in detected]
    authorized = _authorized_family_ids(inp)

    has_contact_request = "R5_USER_REQUESTS_FAMILY_CONTACT" in rule_ids
    has_negative_feedback = "R4_CONSECUTIVE_NEGATIVE_FEEDBACK" in rule_ids

    if has_contact_request:
        inquiry = "你选择了'希望家人联系我'，我们已经记下这个请求。"
        event_type = "family_contact_request"
        event_status = "pending_family_action" if authorized else "pending_authorization"
        notify = bool(authorized)
        reason = (
            "本人明确请求联系家属，且存在有效授权"
            if notify else
            "本人已提出请求，但没有可接收提醒的有效家属授权，"
            "为保护隐私暂不通知，请先完成授权"
        )
        requires_self_confirmation = False
    elif has_negative_feedback:
        share = any(
            f.feedback_type in NEGATIVE_FEEDBACK_TYPES and f.share_with_family
            for f in inp.feedbacks
        )
        notify = share and bool(authorized)
        event_type = "care_attention"
        event_status = "pending_family_action" if notify else "pending_self_confirmation"
        reason = (
            "本人已主动反馈不适并授权分享，按授权通知家属"
            if notify else
            "本人反馈了不适，但未授权分享该反馈或没有有效家属授权，"
            "先询问本人是否希望家人联系"
        )
        inquiry = "我们注意到你最近几次反馈身体不太舒服，希望了解一下你现在的情况。"
        requires_self_confirmation = not notify
    else:
        rule_names = "、".join(d["rule_name"] for d in detected)
        inquiry = (
            f"今天还没有收到你的签到记录，和你平时的生活规律有些不同"
            f"（{rule_names}）。想确认一下你现在的情况。"
        )
        event_type = "care_inquiry"
        event_status = "pending_self_confirmation"
        notify = False
        reason = (
            "系统只识别到生活规律变化，尚未确认本人情况，"
            "按流程先询问本人，不直接通知家属"
        )
        requires_self_confirmation = True

    return {
        "event_type": event_type,
        "event_status": event_status,
        "created_at": as_of_iso,
        "inquiry_text": inquiry,
        "options": deepcopy(CARE_OPTIONS),
        "requires_self_confirmation": requires_self_confirmation,
        "notify_family": notify,
        "notify_family_reason": reason,
        "authorized_family_ids": authorized,
        "related_rules": rule_ids,
        "data_status": credibility.overall_status,
        "explanation": (
            "；".join(d["reason"] for d in detected[:3])
            + "。以上为生活规律观察，不是医疗判断。"
        ),
        "rule_version": cfg.get("rule_version", "1.0.0"),
    }


def apply_feedback(
    event: dict,
    feedback_type: str,
    inp: AnalysisInput | None = None,
    responded_at: str | None = None,
) -> dict:
    """根据本人反馈更新关怀事件状态（后端保存后的对象可直接覆盖）。"""
    if inp is not None and not isinstance(inp, AnalysisInput):
        inp = AnalysisInput.from_dict(inp)

    updated = deepcopy(event)
    updated["user_response"] = feedback_type
    if responded_at is None and inp is not None:
        responded_at = iso_utc(parse_time(inp.as_of))
    updated["responded_at"] = responded_at
    updated["notify_family"] = False

    if feedback_type in {"feeling_good", "busy_today"}:
        updated["event_status"] = "resolved_self_ok"
        updated["notify_family_reason"] = "本人确认情况正常，关怀事件关闭，不通知家属"
    elif feedback_type == "declined_to_answer":
        updated["event_status"] = "awaiting_recheck"
        updated["notify_family_reason"] = "本人暂时不想回答，尊重意愿，稍后重新询问"
    elif feedback_type in {"feeling_unwell", "need_help", CONTACT_REQUEST_FEEDBACK}:
        authorized = _authorized_family_ids(inp) if inp else list(event.get("authorized_family_ids") or [])
        if authorized:
            updated["event_status"] = "pending_family_action"
            updated["notify_family"] = True
            updated["notify_family_reason"] = "本人明确表示需要帮助，且存在有效家属授权"
        else:
            updated["event_status"] = "pending_authorization"
            updated["notify_family_reason"] = "本人需要帮助，但没有有效家属授权，暂不通知"
    else:
        updated["event_status"] = "needs_review"
        updated["notify_family_reason"] = "未知反馈类型，需人工查看"

    return updated


def complete_event(event: dict) -> dict:
    """家属完成联系后调用，标记事件处理完成。"""
    updated = deepcopy(event)
    updated["event_status"] = "completed"
    updated["notify_family"] = False
    return updated
