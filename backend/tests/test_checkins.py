"""签到模块测试：提交、查询、时区转换、鉴权、字段校验。"""

from datetime import datetime, timezone


def test_create_and_read_checkin(client, registered_user):
    """提交签到后能通过历史接口查到，且字段统一。"""
    payload = {
        "check_in_at": "2026-11-26T08:30:00Z",
        "mood": "good",
        "status": "normal",
        "note": "今天状态不错",
        "data_source": "manual",
    }
    create = client.post("/api/v1/checkins", json=payload, headers=registered_user["headers"])
    assert create.status_code == 201
    data = create.json()
    assert data["user_id"] == registered_user["user"]["id"]
    assert data["check_in_at"] == "2026-11-26T08:30:00"
    assert data["mood"] == "good"
    assert data["is_confirmed"] is True

    history = client.get("/api/v1/checkins/me", headers=registered_user["headers"])
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["note"] == "今天状态不错"


def test_checkin_with_timezone_converts_to_utc(client, registered_user):
    """带时区的签到时间必须转换为 UTC 存储。"""
    payload = {"check_in_at": "2026-11-26T16:30:00+08:00", "status": "normal"}
    create = client.post("/api/v1/checkins", json=payload, headers=registered_user["headers"])
    assert create.status_code == 201
    # 16:30 +08:00 = 08:30 UTC
    assert create.json()["check_in_at"] == "2026-11-26T08:30:00"


def test_checkin_requires_auth(client):
    """不带 token 提交签到返回 401。"""
    response = client.post(
        "/api/v1/checkins",
        json={"check_in_at": "2026-11-26T08:30:00Z", "status": "normal"},
    )
    assert response.status_code == 401


def test_checkin_invalid_mood(client, registered_user):
    """非法 mood 返回 400。"""
    response = client.post(
        "/api/v1/checkins",
        json={"check_in_at": "2026-11-26T08:30:00Z", "mood": "happy"},
        headers=registered_user["headers"],
    )
    assert response.status_code == 400


def test_today_checkins(client, registered_user):
    """最近 24 小时的签到出现在 /me/today 中。"""
    payload = {"check_in_at": datetime.now(timezone.utc).isoformat(), "status": "normal"}
    create = client.post("/api/v1/checkins", json=payload, headers=registered_user["headers"])
    assert create.status_code == 201

    today = client.get("/api/v1/checkins/me/today", headers=registered_user["headers"])
    assert today.status_code == 200
    assert len(today.json()) == 1


def test_checkins_isolated_between_users(client, registered_user):
    """用户 A 看不到用户 B 的签到。"""
    client.post(
        "/api/v1/checkins",
        json={"check_in_at": "2026-11-26T08:30:00Z", "status": "normal"},
        headers=registered_user["headers"],
    )

    # 注册第二个用户
    client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "secret123", "display_name": "鲍勃"},
    )
    bob_login = client.post(
        "/api/v1/auth/login", json={"username": "bob", "password": "secret123"}
    )
    bob_headers = {"Authorization": f"Bearer {bob_login.json()['access_token']}"}

    bob_history = client.get("/api/v1/checkins/me", headers=bob_headers)
    assert bob_history.status_code == 200
    assert len(bob_history.json()) == 0
