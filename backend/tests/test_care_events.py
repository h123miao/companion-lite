"""关怀事件与反馈测试：状态流转、授权、一键呼救。"""

import json

import pytest


@pytest.fixture
def family_setup(client):
    """本人 + 家属，完成绑定确认和 care_events 授权。"""
    client.post(
        "/api/v1/auth/register",
        json={"username": "owner2", "password": "secret123", "display_name": "本人", "role": "self"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"username": "family2", "password": "secret123", "display_name": "家属", "role": "family"},
    )
    owner_token = client.post(
        "/api/v1/auth/login", json={"username": "owner2", "password": "secret123"}
    ).json()["access_token"]
    family_token = client.post(
        "/api/v1/auth/login", json={"username": "family2", "password": "secret123"}
    ).json()["access_token"]
    owner_h = {"Authorization": f"Bearer {owner_token}"}
    family_h = {"Authorization": f"Bearer {family_token}"}

    code = client.post("/api/v1/family/invite-code", headers=owner_h).json()["invite_code"]
    link_id = client.post(
        "/api/v1/family/bind", json={"invite_code": code, "relation": "子女"}, headers=family_h
    ).json()["id"]
    client.put(f"/api/v1/family/links/{link_id}/confirm", headers=owner_h)
    client.put(
        f"/api/v1/family/links/{link_id}/permission",
        json={"permission_scope": ["care_events", "feedback"], "can_receive_alert": True},
        headers=owner_h,
    )
    return {"owner": owner_h, "family": family_h, "link_id": link_id}


def test_full_care_loop(client, family_setup):
    """完整闭环：创建事件 -> 询问 -> 回应 -> 通知家属 -> 家属看到 -> 标记联系 -> 关闭。"""
    h = family_setup
    event = client.post(
        "/api/v1/care-events",
        json={
            "event_type": "checkin_delay",
            "trigger_rule": "rule_checkin_time_deviation",
            "reason": "今日签到时间明显晚于本人历史规律，数据同步正常",
            "concern_level": "low",
        },
        headers=h["owner"],
    )
    assert event.status_code == 201
    event_id = event.json()["id"]
    assert event.json()["event_status"] == "pending"

    asked = client.post(f"/api/v1/care-events/{event_id}/ask", headers=h["owner"])
    assert asked.json()["event_status"] == "asking"
    assert asked.json()["asked_at"] is not None

    responded = client.post(
        f"/api/v1/care-events/{event_id}/respond",
        json={"response": "busy"},
        headers=h["owner"],
    )
    assert responded.json()["event_status"] == "answered"
    assert responded.json()["user_response"] == "busy"

    notified = client.post(f"/api/v1/care-events/{event_id}/notify-family", headers=h["owner"])
    assert notified.json()["event_status"] == "family_pending"
    assert notified.json()["family_notified_at"] is not None
    assert notified.json()["family_link_id"] == h["link_id"]

    family_list = client.get("/api/v1/care-events/family", headers=h["family"])
    assert len(family_list.json()) == 1

    contacted = client.post(f"/api/v1/care-events/{event_id}/mark-contacted", headers=h["family"])
    assert contacted.json()["family_contacted_at"] is not None

    closed = client.post(f"/api/v1/care-events/{event_id}/close", headers=h["family"])
    assert closed.json()["event_status"] == "closed"
    assert closed.json()["handled_at"] is not None


def test_response_creates_feedback(client, family_setup):
    """本人回应时自动保存一条用户反馈。"""
    h = family_setup
    event_id = client.post(
        "/api/v1/care-events",
        json={
            "event_type": "feedback_concern",
            "trigger_rule": "rule_feedback",
            "reason": "连续反馈状态不佳",
        },
        headers=h["owner"],
    ).json()["id"]
    client.post(f"/api/v1/care-events/{event_id}/respond", json={"response": "unwell"}, headers=h["owner"])

    feedback = client.get("/api/v1/feedback/me", headers=h["owner"])
    assert len(feedback.json()) == 1
    assert feedback.json()[0]["feedback_type"] == "unwell"
    assert feedback.json()[0]["source"] == "care_response"


def test_sos_creates_emergency_event(client, family_setup):
    """一键呼救创建 is_emergency=true 的紧急事件并通知家属。"""
    h = family_setup
    response = client.post("/api/v1/care-events/sos", headers=h["owner"])
    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "sos"
    assert data["is_emergency"] is True
    assert data["concern_level"] == "high"
    assert data["event_status"] == "family_pending"
    assert data["family_notified_at"] is not None

    family_list = client.get("/api/v1/care-events/family", headers=h["family"])
    assert len(family_list.json()) == 1
    assert family_list.json()[0]["is_emergency"] is True


def test_sos_without_authorized_family(client):
    """没有授权家属时，sos 事件仍创建但状态为 pending。"""
    client.post(
        "/api/v1/auth/register",
        json={"username": "solo", "password": "secret123", "display_name": "独居用户"},
    )
    token = client.post(
        "/api/v1/auth/login", json={"username": "solo", "password": "secret123"}
    ).json()["access_token"]
    response = client.post(
        "/api/v1/care-events/sos", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["event_status"] == "pending"
    assert response.json()["family_link_id"] is None


def test_family_cannot_see_unnotified_event(client, family_setup):
    """家属看不到尚未通知的事件。"""
    h = family_setup
    client.post(
        "/api/v1/care-events",
        json={"event_type": "checkin_delay", "trigger_rule": "r", "reason": "测试"},
        headers=h["owner"],
    )
    assert len(client.get("/api/v1/care-events/family", headers=h["family"]).json()) == 0


def test_unauthorized_family_cannot_access(client, family_setup):
    """未授权 care_events 的家属不能访问事件详情。"""
    h = family_setup
    event_id = client.post(
        "/api/v1/care-events",
        json={"event_type": "checkin_delay", "trigger_rule": "r", "reason": "测试"},
        headers=h["owner"],
    ).json()["id"]

    # 撤销授权
    client.delete(f"/api/v1/family/links/{h['link_id']}", headers=h["owner"])

    assert client.get(f"/api/v1/care-events/{event_id}", headers=h["family"]).status_code == 403


def test_invalid_response_rejected(client, family_setup):
    """非法的回应选项返回 400。"""
    h = family_setup
    event_id = client.post(
        "/api/v1/care-events",
        json={"event_type": "checkin_delay", "trigger_rule": "r", "reason": "测试"},
        headers=h["owner"],
    ).json()["id"]
    assert client.post(
        f"/api/v1/care-events/{event_id}/respond",
        json={"response": "maybe"},
        headers=h["owner"],
    ).status_code == 400


def test_manual_feedback(client, family_setup):
    """用户主动提交反馈。"""
    h = family_setup
    response = client.post(
        "/api/v1/feedback",
        json={"feedback_type": "want_family_contact", "content": "希望孩子联系我"},
        headers=h["owner"],
    )
    assert response.status_code == 201
    assert response.json()["feedback_type"] == "want_family_contact"
    assert response.json()["source"] == "manual"


def test_event_is_visible_only_to_targeted_family(client, family_setup):
    """有多位已授权家属时，未收到该事件的家属不能查看或处理它。"""
    h = family_setup
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "family_extra",
            "password": "secret123",
            "display_name": "第二位家属",
            "role": "family",
        },
    )
    extra_headers = {
        "Authorization": "Bearer "
        + client.post(
            "/api/v1/auth/login",
            json={"username": "family_extra", "password": "secret123"},
        ).json()["access_token"]
    }
    code = client.post(
        "/api/v1/family/invite-code", headers=h["owner"]
    ).json()["invite_code"]
    extra_link_id = client.post(
        "/api/v1/family/bind",
        json={"invite_code": code},
        headers=extra_headers,
    ).json()["id"]
    client.put(f"/api/v1/family/links/{extra_link_id}/confirm", headers=h["owner"])
    client.put(
        f"/api/v1/family/links/{extra_link_id}/permission",
        json={"permission_scope": ["care_events"], "can_receive_alert": True},
        headers=h["owner"],
    )

    event_id = client.post(
        "/api/v1/care-events",
        json={"event_type": "checkin_delay", "trigger_rule": "r", "reason": "测试"},
        headers=h["owner"],
    ).json()["id"]
    client.post(f"/api/v1/care-events/{event_id}/ask", headers=h["owner"])
    client.post(
        f"/api/v1/care-events/{event_id}/respond",
        json={"response": "busy"},
        headers=h["owner"],
    )
    notified = client.post(
        f"/api/v1/care-events/{event_id}/notify-family", headers=h["owner"]
    ).json()

    if notified["family_link_id"] == h["link_id"]:
        untargeted = extra_headers
    else:
        untargeted = h["family"]

    assert client.get(
        f"/api/v1/care-events/{event_id}", headers=untargeted
    ).status_code == 403
    assert client.post(
        f"/api/v1/care-events/{event_id}/close", headers=untargeted
    ).status_code == 403
    assert all(
        event["id"] != event_id
        for event in client.get(
            "/api/v1/care-events/family", headers=untargeted
        ).json()
    )


def test_alert_switch_must_be_enabled(client, family_setup):
    """仅授权 care_events 但关闭提醒时，不能向该家属发送事件。"""
    h = family_setup
    client.put(
        f"/api/v1/family/links/{h['link_id']}/permission",
        json={"permission_scope": ["care_events"], "can_receive_alert": False},
        headers=h["owner"],
    )
    event_id = client.post(
        "/api/v1/care-events",
        json={"event_type": "checkin_delay", "trigger_rule": "r", "reason": "测试"},
        headers=h["owner"],
    ).json()["id"]
    notified = client.post(
        f"/api/v1/care-events/{event_id}/notify-family", headers=h["owner"]
    )
    assert notified.status_code == 400

    sos = client.post("/api/v1/care-events/sos", headers=h["owner"])
    assert sos.status_code == 201
    assert sos.json()["event_status"] == "pending"
    assert sos.json()["family_link_id"] is None


def test_cannot_respond_after_event_closed(client, family_setup):
    h = family_setup
    event_id = client.post(
        "/api/v1/care-events",
        json={"event_type": "checkin_delay", "trigger_rule": "r", "reason": "测试"},
        headers=h["owner"],
    ).json()["id"]
    assert client.post(
        f"/api/v1/care-events/{event_id}/close", headers=h["owner"]
    ).status_code == 200
    response = client.post(
        f"/api/v1/care-events/{event_id}/respond",
        json={"response": "fine"},
        headers=h["owner"],
    )
    assert response.status_code == 409
