"""基线与看板测试：数据不足保护、基线计算、授权过滤。"""

from datetime import timedelta

import pytest

from app.core.time_utils import utcnow


@pytest.fixture
def owner_family(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "own3", "password": "secret123", "display_name": "本人", "role": "self"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"username": "fam3", "password": "secret123", "display_name": "家属", "role": "family"},
    )
    oh = {"Authorization": "Bearer " + client.post(
        "/api/v1/auth/login", json={"username": "own3", "password": "secret123"}
    ).json()["access_token"]}
    fh = {"Authorization": "Bearer " + client.post(
        "/api/v1/auth/login", json={"username": "fam3", "password": "secret123"}
    ).json()["access_token"]}

    code = client.post("/api/v1/family/invite-code", headers=oh).json()["invite_code"]
    link_id = client.post(
        "/api/v1/family/bind", json={"invite_code": code}, headers=fh
    ).json()["id"]
    client.put(f"/api/v1/family/links/{link_id}/confirm", headers=oh)
    return {"owner": oh, "family": fh, "link_id": link_id,
            "owner_id": client.get("/api/v1/auth/me", headers=oh).json()["id"]}


def test_baseline_insufficient_data(client, owner_family):
    """数据不足时 data_sufficient=false，不产生变化结论。"""
    h = owner_family
    client.post(
        "/api/v1/checkins",
        json={"check_in_at": utcnow().isoformat(), "status": "normal"},
        headers=h["owner"],
    )
    profile = client.post("/api/v1/baselines/me/recalculate", headers=h["owner"])
    assert profile.status_code == 200
    assert profile.json()["data_sufficient"] is False
    assert profile.json()["valid_days"] == 1


def test_baseline_sufficient_data(client, owner_family):
    """8 天签到数据后，按北京时间计算基线。"""
    h = owner_family
    for day in range(8):
        # 00:15 UTC 等于北京时间 08:15。
        checkin_time = (utcnow() - timedelta(days=day)).replace(
            hour=0, minute=15, second=0
        )
        client.post(
            "/api/v1/checkins",
            json={"check_in_at": checkin_time.isoformat() + "Z", "status": "normal"},
            headers=h["owner"],
        )
    profile = client.post("/api/v1/baselines/me/recalculate", headers=h["owner"])
    assert profile.json()["data_sufficient"] is True
    assert profile.json()["valid_days"] == 8
    assert profile.json()["checkin_time_median"] == "08:15:00"


def test_baseline_uses_user_timezone(client, owner_family):
    """同样的 UTC 时间在不同用户时区下应得到不同本地签到时间。"""
    h = owner_family
    client.put(
        "/api/v1/auth/me",
        json={"timezone": "UTC"},
        headers=h["owner"],
    )
    for day in range(8):
        checkin_time = (utcnow() - timedelta(days=day)).replace(
            hour=8, minute=15, second=0
        )
        client.post(
            "/api/v1/checkins",
            json={"check_in_at": checkin_time.isoformat() + "Z", "status": "normal"},
            headers=h["owner"],
        )
    profile = client.post("/api/v1/baselines/me/recalculate", headers=h["owner"])
    assert profile.json()["checkin_time_median"] == "08:15:00"


def test_self_dashboard(client, owner_family):
    """本人看板包含签到、活动、数据状态。"""
    h = owner_family
    client.post(
        "/api/v1/checkins",
        json={"check_in_at": utcnow().isoformat(), "status": "normal", "mood": "good"},
        headers=h["owner"],
    )
    dashboard = client.get("/api/v1/dashboard/self", headers=h["owner"])
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert len(data["recent_checkins"]) == 1
    assert "data_status" in data
    assert "note" in data["data_status"]


def test_family_dashboard_no_scope(client, owner_family):
    """家属未获授权时看不到任何本人数据。"""
    h = owner_family
    client.post(
        "/api/v1/checkins",
        json={"check_in_at": utcnow().isoformat(), "status": "normal"},
        headers=h["owner"],
    )
    dashboard = client.get(f"/api/v1/dashboard/family/{h['owner_id']}", headers=h["family"])
    assert dashboard.status_code == 200
    assert "recent_checkins" not in dashboard.json()
    assert dashboard.json()["authorized_scopes"] == []


def test_family_dashboard_with_scope(client, owner_family):
    """授权 checkins 后家属能看到签到，但仍看不到活动。"""
    h = owner_family
    client.post(
        "/api/v1/checkins",
        json={"check_in_at": utcnow().isoformat(), "status": "normal"},
        headers=h["owner"],
    )
    client.post(
        "/api/v1/activities",
        json={"activity_type": "meal", "recorded_at": utcnow().isoformat()},
        headers=h["owner"],
    )
    client.put(
        f"/api/v1/family/links/{h['link_id']}/permission",
        json={"permission_scope": ["checkins"]},
        headers=h["owner"],
    )
    dashboard = client.get(f"/api/v1/dashboard/family/{h['owner_id']}", headers=h["family"])
    data = dashboard.json()
    assert len(data["recent_checkins"]) == 1
    assert "recent_activities" not in data


def test_family_dashboard_unbound(client, owner_family):
    """未绑定的家属访问他人看板返回 403。"""
    h = owner_family
    client.post(
        "/api/v1/auth/register",
        json={"username": "stranger", "password": "secret123", "display_name": "陌生人", "role": "family"},
    )
    sh = {"Authorization": "Bearer " + client.post(
        "/api/v1/auth/login", json={"username": "stranger", "password": "secret123"}
    ).json()["access_token"]}
    assert client.get(f"/api/v1/dashboard/family/{h['owner_id']}", headers=sh).status_code == 403


def test_data_status_distinguishes_offline(client, owner_family):
    """设备离线时数据状态明确说明，不判断为危险。"""
    h = owner_family
    client.post(
        "/api/v1/devices",
        json={"device_type": "xiaomi_watch", "device_id": "W-1"},
        headers=h["owner"],
    )
    device_id = client.get("/api/v1/devices/me", headers=h["owner"]).json()[0]["id"]
    client.put(f"/api/v1/devices/{device_id}/status", json={"status": "offline"}, headers=h["owner"])

    dashboard = client.get("/api/v1/dashboard/self", headers=h["owner"])
    note = dashboard.json()["data_status"]["note"]
    assert "设备离线" in note
    assert "不代表没有活动" in note


def test_detect_changes_saves_event_without_duplicates(client, owner_family):
    """变化识别接口保存关怀事件，同一未关闭规则不重复创建。"""
    h = owner_family
    for day in range(1, 9):
        checkin_time = (utcnow() - timedelta(days=day)).replace(
            hour=0, minute=15, second=0
        )
        client.post(
            "/api/v1/checkins",
            json={"check_in_at": checkin_time.isoformat() + "Z", "status": "normal"},
            headers=h["owner"],
        )
    baseline = client.post("/api/v1/baselines/me/recalculate", headers=h["owner"])
    assert baseline.json()["data_sufficient"] is True

    late_today = utcnow().replace(hour=10, minute=0, second=0)
    client.post(
        "/api/v1/checkins",
        json={"check_in_at": late_today.isoformat() + "Z", "status": "normal"},
        headers=h["owner"],
    )
    first = client.post("/api/v1/baselines/me/detect-changes", headers=h["owner"])
    assert first.status_code == 200
    assert len(first.json()) == 1
    assert first.json()[0]["trigger_rule"] == "rule_checkin_time_deviation"

    second = client.post("/api/v1/baselines/me/detect-changes", headers=h["owner"])
    assert second.status_code == 200
    assert second.json() == []
