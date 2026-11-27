"""家庭关系与授权测试：邀请码、绑定、确认、授权范围、撤销。"""

import pytest


@pytest.fixture
def owner_and_family(client):
    """创建本人和家属两个账号。"""
    client.post(
        "/api/v1/auth/register",
        json={"username": "owner", "password": "secret123", "display_name": "本人", "role": "self"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"username": "family", "password": "secret123", "display_name": "家属", "role": "family"},
    )
    owner_token = client.post(
        "/api/v1/auth/login", json={"username": "owner", "password": "secret123"}
    ).json()["access_token"]
    family_token = client.post(
        "/api/v1/auth/login", json={"username": "family", "password": "secret123"}
    ).json()["access_token"]
    return {
        "owner": {"Authorization": f"Bearer {owner_token}"},
        "family": {"Authorization": f"Bearer {family_token}"},
    }


def test_full_binding_flow(client, owner_and_family):
    """完整流程：生成邀请码 -> 家属绑定 -> 本人确认 -> 设置授权。"""
    h = owner_and_family

    code = client.post("/api/v1/family/invite-code", headers=h["owner"])
    assert code.status_code == 200
    invite_code = code.json()["invite_code"]
    assert len(invite_code) == 6

    bind = client.post(
        "/api/v1/family/bind",
        json={"invite_code": invite_code, "relation": "子女"},
        headers=h["family"],
    )
    assert bind.status_code == 201
    link_id = bind.json()["id"]
    assert bind.json()["status"] == "pending"

    confirm = client.put(f"/api/v1/family/links/{link_id}/confirm", headers=h["owner"])
    assert confirm.status_code == 200
    assert confirm.json()["status"] == "active"

    perm = client.put(
        f"/api/v1/family/links/{link_id}/permission",
        json={"permission_scope": ["checkins", "activities"], "can_receive_alert": True},
        headers=h["owner"],
    )
    assert perm.status_code == 200
    assert "checkins" in perm.json()["permission_scope"]
    assert perm.json()["can_receive_alert"] is True


def test_family_cannot_generate_invite_code(client, owner_and_family):
    """家属不能生成邀请码。"""
    response = client.post("/api/v1/family/invite-code", headers=owner_and_family["family"])
    assert response.status_code == 403


def test_invalid_invite_code(client, owner_and_family):
    """无效邀请码返回 400。"""
    response = client.post(
        "/api/v1/family/bind",
        json={"invite_code": "ZZZZZZ", "relation": "子女"},
        headers=owner_and_family["family"],
    )
    assert response.status_code == 400


def test_invite_code_single_use(client, owner_and_family):
    """邀请码用一次后作废。"""
    h = owner_and_family
    code = client.post("/api/v1/family/invite-code", headers=h["owner"]).json()["invite_code"]
    client.post(
        "/api/v1/family/bind", json={"invite_code": code}, headers=h["family"]
    )
    second = client.post(
        "/api/v1/family/bind", json={"invite_code": code}, headers=h["family"]
    )
    assert second.status_code == 400


def test_only_owner_can_confirm(client, owner_and_family):
    """家属不能自己确认绑定。"""
    h = owner_and_family
    code = client.post("/api/v1/family/invite-code", headers=h["owner"]).json()["invite_code"]
    link_id = client.post(
        "/api/v1/family/bind", json={"invite_code": code}, headers=h["family"]
    ).json()["id"]
    response = client.put(f"/api/v1/family/links/{link_id}/confirm", headers=h["family"])
    assert response.status_code == 403


def test_revoke_permission(client, owner_and_family):
    """撤销授权后 status 变为 revoked，授权范围清空。"""
    h = owner_and_family
    code = client.post("/api/v1/family/invite-code", headers=h["owner"]).json()["invite_code"]
    link_id = client.post(
        "/api/v1/family/bind", json={"invite_code": code}, headers=h["family"]
    ).json()["id"]
    client.put(f"/api/v1/family/links/{link_id}/confirm", headers=h["owner"])
    client.put(
        f"/api/v1/family/links/{link_id}/permission",
        json={"permission_scope": ["checkins"]},
        headers=h["owner"],
    )
    revoke = client.delete(f"/api/v1/family/links/{link_id}", headers=h["owner"])
    assert revoke.status_code == 200
    assert revoke.json()["status"] == "revoked"
    assert revoke.json()["permission_scope"] == []


def test_invalid_scope_rejected(client, owner_and_family):
    """非法的授权类型返回 400。"""
    h = owner_and_family
    code = client.post("/api/v1/family/invite-code", headers=h["owner"]).json()["invite_code"]
    link_id = client.post(
        "/api/v1/family/bind", json={"invite_code": code}, headers=h["family"]
    ).json()["id"]
    client.put(f"/api/v1/family/links/{link_id}/confirm", headers=h["owner"])
    response = client.put(
        f"/api/v1/family/links/{link_id}/permission",
        json={"permission_scope": ["all_data"]},
        headers=h["owner"],
    )
    assert response.status_code == 400
