"""活动记录测试：创建、查询、筛选、修改、删除、权限隔离。"""

import pytest


@pytest.fixture
def user_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "actuser", "password": "secret123", "display_name": "活动用户"},
    )
    token = client.post(
        "/api/v1/auth/login", json={"username": "actuser", "password": "secret123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_activity(client, user_headers):
    response = client.post(
        "/api/v1/activities",
        json={"activity_type": "meal", "recorded_at": "2026-11-26T12:05:00Z", "note": "午饭"},
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["activity_type"] == "meal"
    assert response.json()["is_confirmed"] is True

    listing = client.get("/api/v1/activities/me", headers=user_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_filter_by_type(client, user_headers):
    for t in ["meal", "exercise", "meal"]:
        client.post(
            "/api/v1/activities",
            json={"activity_type": t, "recorded_at": "2026-11-26T12:05:00Z"},
            headers=user_headers,
        )
    meals = client.get("/api/v1/activities/me?activity_type=meal", headers=user_headers)
    assert len(meals.json()) == 2


def test_invalid_activity_type(client, user_headers):
    response = client.post(
        "/api/v1/activities",
        json={"activity_type": "flying", "recorded_at": "2026-11-26T12:05:00Z"},
        headers=user_headers,
    )
    assert response.status_code == 400


def test_update_activity(client, user_headers):
    activity_id = client.post(
        "/api/v1/activities",
        json={"activity_type": "meal", "recorded_at": "2026-11-26T12:05:00Z"},
        headers=user_headers,
    ).json()["id"]
    response = client.put(
        f"/api/v1/activities/{activity_id}",
        json={"activity_type": "exercise", "note": "改为运动"},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json()["activity_type"] == "exercise"
    assert response.json()["note"] == "改为运动"


def test_delete_activity(client, user_headers):
    activity_id = client.post(
        "/api/v1/activities",
        json={"activity_type": "rest", "recorded_at": "2026-11-26T13:00:00Z"},
        headers=user_headers,
    ).json()["id"]
    assert client.delete(f"/api/v1/activities/{activity_id}", headers=user_headers).status_code == 204
    assert len(client.get("/api/v1/activities/me", headers=user_headers).json()) == 0


def test_cannot_modify_others_activity(client, user_headers):
    activity_id = client.post(
        "/api/v1/activities",
        json={"activity_type": "meal", "recorded_at": "2026-11-26T12:05:00Z"},
        headers=user_headers,
    ).json()["id"]

    client.post(
        "/api/v1/auth/register",
        json={"username": "other", "password": "secret123", "display_name": "其他人"},
    )
    other_token = client.post(
        "/api/v1/auth/login", json={"username": "other", "password": "secret123"}
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    assert client.put(
        f"/api/v1/activities/{activity_id}",
        json={"note": "篡改"},
        headers=other_headers,
    ).status_code == 403
