"""家庭关系相关请求/响应模型。"""

import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_SCOPES = {"checkins", "activities", "health", "care_events", "feedback", "baseline"}


class InviteCodeOut(BaseModel):
    """本人生成的邀请码。"""

    invite_code: str
    expires_in_minutes: int = 60


class FamilyBindIn(BaseModel):
    """家属用邀请码申请绑定。"""

    invite_code: str = Field(min_length=6, max_length=6)
    relation: str | None = Field(default=None, max_length=20)


class FamilyLinkOut(BaseModel):
    """家庭关系响应。授权范围统一返回 JSON 数组，不向客户端暴露存储细节。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    family_id: int
    relation: str | None = None
    status: str
    permission_scope: list[str] = Field(default_factory=list)
    can_receive_alert: bool
    requested_at: datetime
    confirmed_at: datetime | None = None
    revoked_at: datetime | None = None

    @field_validator("permission_scope", mode="before")
    @classmethod
    def parse_permission_scope(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return []
        return [item for item in parsed if item in VALID_SCOPES] if isinstance(parsed, list) else []


class PermissionUpdate(BaseModel):
    """本人设置家属的授权范围。"""

    permission_scope: list[str] = Field(default_factory=list)
    can_receive_alert: bool = False
