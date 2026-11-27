"""用户相关的请求/响应模型。"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.time_utils import validate_timezone_name


class UserRegister(BaseModel):
    """注册请求。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128, description="至少 6 位")
    display_name: str = Field(min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    role: str = Field(default="self", description="self=本人, family=家属")
    timezone: str = Field(default="Asia/Shanghai", max_length=50)

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, value: str) -> str:
        return validate_timezone_name(value)


class UserUpdate(BaseModel):
    """本人可修改的资料。用户名和角色不允许在这里修改。"""

    display_name: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    gender: str | None = Field(default=None, max_length=10)
    birth_date: date | None = None
    timezone: str | None = Field(default=None, max_length=50)

    @field_validator("timezone")
    @classmethod
    def check_optional_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_timezone_name(value)


class UserLogin(BaseModel):
    """登录请求。"""

    username: str
    password: str


class UserOut(BaseModel):
    """用户信息响应（不含密码哈希）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    role: str
    phone: str | None = None
    email: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    timezone: str
    status: str
    created_at: datetime


class Token(BaseModel):
    """登录成功返回的 JWT。"""

    access_token: str
    token_type: str = "bearer"
