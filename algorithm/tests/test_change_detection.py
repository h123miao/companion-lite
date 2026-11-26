"""变化识别测试：每条规则命中都要有可解释的原因与数据状态。"""
from companion_algo.baseline import compute_baseline
from companion_algo.change_detection import detect_changes
from companion_algo.credibility import assess_credibility
from companion_algo.schema import AnalysisInput
from testdata.generate_test_data import load_cases

CASES = {c["user_id"]: c for c in load_cases()}


def run(user_id):
    inp = AnalysisInput.from_dict(CASES[user_id]["input"])
    baseline = compute_baseline(inp)
    credibility = assess_credibility(inp, baseline)
    changes = detect_changes(inp, baseline, credibility)
    return inp, baseline, credibility, changes


def test_normal_and_late_riser_have_no_false_positive():
    for user_id in (1001, 1002, 1003, 1005):
        _, _, _, changes = run(user_id)
        assert changes["detected"] == [], f"用户 {user_id} 出现误报: {changes['detected']}"


def test_consecutive_missing_triggers_r1_and_r3():
    _, _, credibility, changes = run(1004)
    ids = {d["rule_id"] for d in changes["detected"]}
    assert "R1_CHECKIN_TIME_DEVIATION" in ids
    assert "R3_CONSECUTIVE_MISSING_CHECKINS" in ids
    assert all(d["data_status"] == credibility.overall_status for d in changes["detected"])
    assert all(d["reason"] and d["data_used"] for d in changes["detected"])


def test_sync_delay_changes_are_marked_as_uncertain():
    _, _, _, changes = run(1006)
    r1 = [d for d in changes["detected"] if d["rule_id"] == "R1_CHECKIN_TIME_DEVIATION"]
    assert len(r1) == 1
    assert r1[0]["data_status"] == "sync_delay"
    assert "不能" in r1[0]["reason"] or "未送达" in r1[0]["reason"]


def test_activity_drop_triggers_r2():
    _, _, _, changes = run(1010)
    ids = {d["rule_id"] for d in changes["detected"]}
    assert "R2_ACTIVITY_COUNT_DROP" in ids


def test_negative_feedback_triggers_r4():
    _, _, _, changes = run(1007)
    ids = {d["rule_id"] for d in changes["detected"]}
    assert "R4_CONSECUTIVE_NEGATIVE_FEEDBACK" in ids


def test_contact_request_triggers_r5():
    _, _, _, changes = run(1009)
    ids = {d["rule_id"] for d in changes["detected"]}
    assert "R5_USER_REQUESTS_FAMILY_CONTACT" in ids


def test_insufficient_history_suppresses_all_rules():
    _, _, _, changes = run(1008)
    assert changes["detected"] == []
    assert len(changes["suppressed"]) == 5
    assert all("数据不足" in s["reason"] for s in changes["suppressed"])
