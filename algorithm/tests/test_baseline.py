"""基线算法测试：验证统计结果符合预期，数据不足时拒绝判断。"""
from datetime import datetime, timedelta, timezone

from companion_algo.baseline import compute_baseline
from companion_algo.schema import AnalysisInput
from companion_algo.utils import parse_time
from testdata.generate_test_data import load_cases

CASES = {c["user_id"]: c for c in load_cases()}


def case_input(user_id):
    return AnalysisInput.from_dict(CASES[user_id]["input"])


def test_normal_user_baseline_is_sufficient():
    result = compute_baseline(case_input(1001))
    assert result.sufficient is True
    assert result.coverage_days >= 7


def test_normal_user_median_is_around_eight():
    result = compute_baseline(case_input(1001))
    # 模拟数据在 08:00—08:20 之间，中位数应落在 480—500 分钟
    assert 480 <= result.checkin_median_min <= 500
    assert result.to_dict()["checkin_time_median"].startswith("08:")


def test_late_riser_baseline_is_later_than_normal_user():
    normal = compute_baseline(case_input(1001))
    late = compute_baseline(case_input(1002))
    assert late.checkin_median_min - normal.checkin_median_min > 120


def test_insufficient_history_returns_reason():
    result = compute_baseline(case_input(1008))
    assert result.sufficient is False
    assert "数据不足" in result.insufficient_reason
    assert result.to_dict()["checkin_time_median"] is None


def test_early_morning_checkin_is_normalized():
    """凌晨 01:00 签到应被视为次日凌晨，避免与 23:30 求平均拉偏。"""
    as_of = "2026-11-26T10:00:00Z"
    base = parse_time(as_of)
    checkins = []
    for i in range(10):
        day = base - timedelta(days=i + 1)
        local = datetime(day.year, day.month, day.day, 1, 0,
                         tzinfo=timezone(timedelta(hours=8)))
        checkins.append({
            "check_in_at": local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        })
    result = compute_baseline(AnalysisInput.from_dict({
        "user_id": 1, "as_of": as_of, "checkins": checkins
    }))
    assert result.sufficient is True
    assert result.checkin_median_min >= 1440
    assert result.to_dict()["checkin_time_median"] == "01:00"
