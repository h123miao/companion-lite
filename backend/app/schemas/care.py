"""关怀事件与反馈相关模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

EVENT_TYPES = {"checkin_delay", "activity_drop", "feedback_concern", "user_request", "sos"}
CONCERN_LEVELS = {"low", "medium", "high"}
USER_RESPONSES = {"fine", "busy", "unwell", "want_family_contact", "no_answer"}
FEEDBACK_TYPES = USER_RESPONSES | {"other"}


class CareEventCreate(BaseModel):
    """通常由算法或本人触发创建。"""

    event_type: str
    trigger_rule: str = Field(max_length=50)
    concern_level: str = Field(default="low")
    reason: str = Field(min_length=1)
    evidence: str | None = None


class CareEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    family_link_id: int | None = None
    event_type: str
    is_emergency: bool
    trigger_rule: str
    event_status: str
    concern_level: str
    reason: str
    evidence: str | None = None
    asked_at: datetime | None = None
    user_response: str | None = None
    responded_at: datetime | None = None
    family_notified_at: datetime | None = None
    family_contacted_at: datetime | None = None
    handled_at: datetime | None = None
    created_at: datetime


class RespondIn(BaseModel):
    """本人回应关怀询问。"""

    response: str = Field(description="fine/busy/unwell/want_family_contact/no_answer")


class FeedbackCreate(BaseModel):
    feedback_type: str = Field(description="fine/busy/unwell/want_family_contact/no_answer/other")
    content: str | None = Field(default=None, max_length=500)
    care_event_id: int | None = None


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    care_event_id: int | None = None
    feedback_type: str
    content: str | None = None
    source: str
    created_at: datetime
