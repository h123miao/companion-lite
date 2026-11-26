"""数据可信度测试：六种状态必须能区分，且绝不输出危险结论。"""
from companion_algo.baseline import compute_baseline
from companion_algo.credibility import assess_credibility
from companion_algo.schema import AnalysisInput
from testdata.generate_test_data import load_cases

CASES = {c["user_id"]: c for c in load_cases()}


def report_for(user_id):
    inp = AnalysisInput.from_dict(CASES[user_id]["input"])
    baseline = compute_baseline(inp)
    return assess_credibility(inp, baseline)


def test_normal_user_is_normal():
    report = report_for(1001)
    assert report.overall_status == "normal"
    assert report.insufficient is False


def test_device_offline_is_distinguished_from_missing():
    report = report_for(1005)
    assert report.device_status == "device_offline"
    assert report.checkin_status == "normal"  # 本人已签到，手表离线不等于用户没活动
    assert "不能解释为用户没有活动" in "".join(report.reasons)


def test_sync_delay_is_distinguished():
    report = report_for(1006)
    assert report.health_status == "sync_delay"
    assert report.overall_status == "sync_delay"


def test_user_feedback_has_highest_priority():
    report = report_for(1007)
    assert report.overall_status == "user_feedback"


def test_missing_checkin_never_becomes_danger_claim():
    report = report_for(1004)
    assert report.checkin_status == "missing_unknown"
    text = "".join(report.reasons)
    assert "不等于用户有危险" in text
    for word in ("危险结论", "发生意外", "急救", "疾病"):
        assert word not in text


def test_insufficient_data_blocks_analysis():
    report = report_for(1008)
    assert report.insufficient is True
    assert report.overall_status == "insufficient"
