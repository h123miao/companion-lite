"""设备/健康数据/同步日志测试。"""

import pytest


@pytest.fixture
def user_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "devuser", "password": "secret123", "display_name": "设备用户"},
    )
    token = client.post(
        "/api/v1/auth/login", json={"username": "devuser", "password": "secret123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_bind_and_list_device(client, user_headers):
    response = client.post(
        "/api/v1/devices",
        json={"device_type": "xiaomi_watch", "device_id": "MI-12345", "device_name": "小米手环"},
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["status"] == "active"

    listing = client.get("/api/v1/devices/me", headers=user_headers)
    assert len(listing.json()) == 1


def test_invalid_device_type(client, user_headers):
    response = client.post(
        "/api/v1/devices",
        json={"device_type": "apple", "device_id": "X-1"},
        headers=user_headers,
    )
    assert response.status_code == 400


def test_device_offline_status(client, user_headers):
    device_id = client.post(
        "/api/v1/devices",
        json={"device_type": "xiaomi_watch", "device_id": "MI-1"},
        headers=user_headers,
    ).json()["id"]
    response = client.put(
        f"/api/v1/devices/{device_id}/status",
        json={"status": "offline"},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "offline"


def test_health_record_with_device(client, user_headers):
    device_id = client.post(
        "/api/v1/devices",
        json={"device_type": "xiaomi_watch", "device_id": "MI-2"},
        headers=user_headers,
    ).json()["id"]
    response = client.post(
        "/api/v1/health-records",
        json={
            "data_type": "steps",
            "value": 8234,
            "device_binding_id": device_id,
            "collected_at": "2026-11-26T20:00:00Z",
        },
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["unit"] == "steps"
    assert response.json()["is_valid"] is True


def test_heart_rate_record_no_alarm(client, user_headers):
    """心率数据只记录，不产生任何报警字段。"""
    response = client.post(
        "/api/v1/health-records",
        json={"data_type": "heart_rate", "value": 78, "collected_at": "2026-11-26T20:00:00Z"},
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["unit"] == "bpm"
    data = response.json()
    assert "alarm" not in data
    assert "is_abnormal" not in data


def test_invalid_health_type(client, user_headers):
    response = client.post(
        "/api/v1/health-records",
        json={"data_type": "blood_pressure", "value": 120, "collected_at": "2026-11-26T20:00:00Z"},
        headers=user_headers,
    )
    assert response.status_code == 400


def test_foreign_device_rejected(client, user_headers):
    """不能用别人的设备上报数据。"""
    device_id = client.post(
        "/api/v1/devices",
        json={"device_type": "other", "device_id": "D-1"},
        headers=user_headers,
    ).json()["id"]
    client.post(
        "/api/v1/auth/register",
        json={"username": "otherdev", "password": "secret123", "display_name": "其他用户"},
    )
    other_token = client.post(
        "/api/v1/auth/login", json={"username": "otherdev", "password": "secret123"}
    ).json()["access_token"]
    response = client.post(
        "/api/v1/health-records",
        json={
            "data_type": "steps",
            "value": 100,
            "device_binding_id": device_id,
            "collected_at": "2026-11-26T20:00:00Z",
        },
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 400


def test_sync_log(client, user_headers):
    response = client.post(
        "/api/v1/sync-logs",
        json={
            "sync_type": "device",
            "status": "success",
            "started_at": "2026-11-26T20:00:00Z",
            "finished_at": "2026-11-26T20:01:00Z",
            "records_count": 30,
        },
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["records_count"] == 30

    logs = client.get("/api/v1/sync-logs/me", headers=user_headers)
    assert len(logs.json()) == 1


def test_invalid_data_source_rejected(client, user_headers):
    """数据来源和同步状态只能使用团队约定的值。"""
    checkin = client.post(
        "/api/v1/checkins",
        json={
            "check_in_at": "2026-11-26T08:30:00Z",
            "data_source": "made_up",
        },
        headers=user_headers,
    )
    assert checkin.status_code == 400

    health = client.post(
        "/api/v1/health-records",
        json={
            "data_type": "steps",
            "value": 100,
            "collected_at": "2026-11-26T20:00:00Z",
            "sync_status": "unknown",
        },
        headers=user_headers,
    )
    assert health.status_code == 400


def test_health_upload_time_cannot_precede_collection(client, user_headers):
    response = client.post(
        "/api/v1/health-records",
        json={
            "data_type": "steps",
            "value": 100,
            "collected_at": "2026-11-26T20:00:00Z",
            "uploaded_at": "2026-11-26T19:00:00Z",
        },
        headers=user_headers,
    )
    assert response.status_code == 400


def test_sync_log_cannot_reference_another_users_device(client, user_headers):
    """同步日志和健康数据一样，必须验证设备归属。"""
    other_device = client.post(
        "/api/v1/devices",
        json={"device_type": "other", "device_id": "OTHER-SYNC"},
        headers=user_headers,
    )
    assert other_device.status_code == 201
    client.post(
        "/api/v1/auth/register",
        json={"username": "syncstranger", "password": "secret123", "display_name": "陌生人"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"username": "syncstranger", "password": "secret123"},
    ).json()["access_token"]
    stranger_headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/sync-logs",
        json={
            "sync_type": "device",
            "status": "success",
            "device_binding_id": other_device.json()["id"],
            "started_at": "2026-11-26T20:00:00Z",
        },
        headers=stranger_headers,
    )
    assert response.status_code == 400
