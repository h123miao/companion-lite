"""认证接口：注册、登录、获取当前用户。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserOut, UserRegister, UserUpdate

router = APIRouter(prefix="/auth", tags=["认证"])

VALID_ROLES = {"self", "family"}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """注册新用户。用户名、手机号、邮箱不能与已有用户重复。"""
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="role 只能是 self 或 family")

    conditions = [User.username == payload.username]
    if payload.phone:
        conditions.append(User.phone == payload.phone)
    if payload.email:
        conditions.append(User.email == payload.email)

    exists = db.query(User).filter(or_(*conditions)).first()
    if exists:
        raise HTTPException(status_code=409, detail="用户名、手机号或邮箱已被占用")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        phone=payload.phone,
        email=payload.email,
        role=payload.role,
        timezone=payload.timezone,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="用户名、手机号或邮箱已被占用") from None
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """登录成功返回 JWT。用户名不存在与密码错误返回相同提示，避免泄露信息。"""
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if user.status != "active":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token({"user_id": user.id, "role": user.role})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改本人资料、联系方式和时区。

    时区只影响展示和本地日期统计，数据库中已有的时间戳仍保持 UTC。
    """
    updates = payload.model_dump(exclude_unset=True)
    if "display_name" in updates and updates["display_name"] is None:
        raise HTTPException(status_code=400, detail="display_name 不能为空")

    conditions = []
    if updates.get("phone") is not None:
        conditions.append(User.phone == updates["phone"])
    if updates.get("email") is not None:
        conditions.append(User.email == updates["email"])
    if conditions:
        exists = (
            db.query(User)
            .filter(User.id != current_user.id, or_(*conditions))
            .first()
        )
        if exists:
            raise HTTPException(status_code=409, detail="手机号或邮箱已被占用")

    for field, value in updates.items():
        setattr(current_user, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="手机号或邮箱已被占用") from None
    db.refresh(current_user)
    return current_user
