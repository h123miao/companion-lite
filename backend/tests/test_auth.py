"""认证模块测试：注册、重复注册、登录、密码错误、JWT 校验。"""

from app.core.security import hash_password, verify_password


def test_password_is_hashed():
    """密码必须哈希保存，且能正确校验。"""
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_register_success(client):
    """注册成功返回 201，响应中不含密码哈希。"""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "secret123", "display_name": "爱丽丝"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["role"] == "self"
    assert "password_hash" not in data
    assert "password" not in data


def test_register_duplicate_username(client):
    """重复用户名返回 409。"""
    payload = {"username": "alice", "password": "secret123", "display_name": "爱丽丝"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_register_invalid_role(client):
    """非法角色返回 400。"""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "secret123", "display_name": "鲍勃", "role": "admin"},
    )
    assert response.status_code == 400


def test_login_success(client):
    """正确密码登录返回 JWT。"""
    client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "secret123", "display_name": "爱丽丝"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert len(response.json()["access_token"]) > 20


def test_login_wrong_password(client):
    """错误密码返回 401。"""
    client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "secret123", "display_name": "爱丽丝"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    """不带 token 访问 /auth/me 返回 401。"""
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_with_token(client, registered_user):
    """带 token 访问 /auth/me 返回当前用户。"""
    response = client.get("/api/v1/auth/me", headers=registered_user["headers"])
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_update_profile(client, registered_user):
    """本人可以修改资料和时区，用户名与角色不随普通资料更新改变。"""
    response = client.put(
        "/api/v1/auth/me",
        json={
            "display_name": "新的显示名",
            "phone": "13800000000",
            "timezone": "UTC",
        },
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "新的显示名"
    assert response.json()["timezone"] == "UTC"
    assert response.json()["username"] == "testuser"
    assert response.json()["role"] == "self"


def test_invalid_timezone_rejected(client):
    """非法时区不能进入数据库，避免基线计算在运行时失败。"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "badtime",
            "password": "secret123",
            "display_name": "错误时区",
            "timezone": "Mars/Olympus",
        },
    )
    assert response.status_code == 422
