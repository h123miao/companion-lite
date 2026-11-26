"""主动关怀测试：先问本人、授权才通知、状态流转正确。"""
from companion_algo import analyze, apply_feedback, complete_event
from companion_algo.schema import AnalysisInput
from testdata.generate_test_data import load_cases

CASES = {c["user_id"]: c for c in load_cases()}


def result_for(user_id):
    return analyze(CASES[user_id]["input"])


def test_no_change_means_no_event():
    for user_id in (1001, 1002, 1003, 1005, 1008):
        assert result_for(user_id)["care_event"] is None


def test_missing_checkin_asks_user_first_and_never_notifies_family():
    event = result_for(1004)["care_event"]
    assert event["event_type"] == "care_inquiry"
    assert event["event_status"] == "pending_self_confirmation"
    assert event["requires_self_confirmation"] is True
    assert event["notify_family"] is False
    assert [o["value"] for o in event["options"]] == [
        "feeling_good", "busy_today", "feeling_unwell",
        "want_family_contact", "declined_to_answer",
    ]
    assert "危险" not in event["inquiry_text"]
    assert "医疗" in event["explanation"]  # 明确声明不是医疗判断


def test_authorized_negative_feedback_notifies_family():
    event = result_for(1007)["care_event"]
    assert event["notify_family"] is True
    assert event["authorized_family_ids"] == [2001]


def test_contact_request_without_authorization_does_not_notify():
    event = result_for(1009)["care_event"]
    assert event["event_type"] == "family_contact_request"
    assert event["notify_family"] is False
    assert event["event_status"] == "pending_authorization"


def test_feedback_updates_event_status():
    inp = AnalysisInput.from_dict(CASES[1004]["input"])
    event = result_for(1004)["care_event"]

    ok = apply_feedback(event, "feeling_good", inp)
    assert ok["event_status"] == "resolved_self_ok"
    assert ok["notify_family"] is False

    declined = apply_feedback(event, "declined_to_answer", inp)
    assert declined["event_status"] == "awaiting_recheck"

    need_help = apply_feedback(event, "want_family_contact", inp)
    assert need_help["event_status"] == "pending_family_action"
    assert need_help["notify_family"] is True

    finished = complete_event(need_help)
    assert finished["event_status"] == "completed"


def test_all_results_are_json_serializable_and_marked_simulated():
    import json
    for user_id in CASES:
        payload = json.dumps(result_for(user_id), ensure_ascii=False)
        assert payload
        assert result_for(user_id)["simulated"] is True
        assert "模拟数据" in result_for(user_id)["data_notice"]
