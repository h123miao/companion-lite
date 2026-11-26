"""生成 10 个虚拟用户 × 30 天模拟测试数据。

运行：python testdata/generate_test_data.py
输出：testdata/simulated_profiles.json

重要：所有数据均为模拟数据，文件内 simulated=true，
不得在演示或文档中称为真实设备采集的数据。
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ_LOCAL = timezone(timedelta(hours=8))  # 北京时间
START_DATE = datetime(2026, 10, 28, tzinfo=TZ_LOCAL)
TOTAL_DAYS = 30
LAST_DATE = START_DATE + timedelta(days=TOTAL_DAYS - 1)


def utc_str(day: datetime, hour: int, minute: int = 0) -> str:
    dt = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_checkin(day, hour, minute, rng, *, sync="synced"):
    return {
        "check_in_at": utc_str(day, hour, minute),
        "mood": rng.choice(["good", "normal", "normal"]),
        "status": "normal",
        "note": "模拟签到",
        "data_source": "manual",
        "sync_status": sync,
        "confirmed": True,
    }


def make_activities(day, rng, count=3):
    slots = [(7, 10), (12, 20), (18, 30), (21, 0)]
    types = ["起床", "用餐", "外出", "运动", "回家", "休息"]
    return [
        {
            "activity_type": types[i % len(types)],
            "recorded_at": utc_str(day, *slots[i % len(slots)]),
            "note": "模拟活动记录",
            "data_source": "manual",
            "sync_status": "synced",
        }
        for i in range(count)
    ]


def make_health(day, rng, *, online=True, pending=False):
    if not online:
        return None
    return {
        "metric": "steps",
        "value": rng.randint(2500, 8000),
        "collected_at": utc_str(day, 21, 0),
        "uploaded_at": None if pending else utc_str(day, 21, 5),
        "data_source": "simulated_watch",
        "valid": True,
        "sync_status": "pending" if pending else "synced",
    }


def authorized(*, active=True, can_alert=True):
    return [{
        "family_user_id": 2001,
        "status": "active" if active else "revoked",
        "scope": ["status", "care_events"],
        "can_receive_alerts": can_alert,
    }]


def build_case(user_id, scenario, expected_rules, expected_notify, builder):
    rng = random.Random(user_id)
    data = builder(rng)
    return {
        "user_id": user_id,
        "scenario": scenario,
        "expected_rules": expected_rules,
        "expected_notify_family": expected_notify,
        "input": data,
    }


def base_builder(*, checkin_hour=8, checkin_spread=20, as_of_hour=9,
                 skip_days=(), offline_last=0, pending_last=0,
                 activity_drop_last=0, auth=None, extra_feedbacks=None,
                 history_days=TOTAL_DAYS):
    """构造一个标准用户，再按场景参数注入变化。"""
    def builder(rng):
        checkins, activities, health_records = [], [], []
        first_day = LAST_DATE - timedelta(days=history_days - 1)
        for i in range(history_days):
            day = first_day + timedelta(days=i)
            is_last = i == history_days - 1
            if i in skip_days or (is_last and skip_days and -1 in skip_days):
                continue
            if not (is_last and pending_last):
                minute = rng.randint(0, checkin_spread)
                checkins.append(make_checkin(day, checkin_hour, minute, rng))
            if activity_drop_last and i >= history_days - activity_drop_last:
                continue
            activities.extend(make_activities(day, rng, count=rng.randint(2, 4)))
            if offline_last and i >= history_days - offline_last:
                continue
            health = make_health(day, rng, pending=bool(is_last and pending_last))
            if health:
                health_records.append(health)

        feedbacks = list(extra_feedbacks or [])
        return {
            "user_id": 0,  # 由外层覆盖
            "as_of": utc_str(LAST_DATE, as_of_hour, 0),
            "checkins": checkins,
            "activities": activities,
            "health_records": health_records,
            "device_states": [{
                "device_id": "sim_watch_01",
                "is_online": offline_last == 0,
                "last_seen_at": utc_str(LAST_DATE, 8, 0) if offline_last == 0
                                else utc_str(LAST_DATE - timedelta(days=offline_last), 21, 0),
                "data_source": "simulated_watch",
            }],
            "feedbacks": feedbacks,
            "authorizations": auth if auth is not None else authorized(),
            "simulated": True,
        }
    return builder


def feedback(kind, days_ago, hour=9, share=False):
    return {
        "feedback_type": kind,
        "created_at": utc_str(LAST_DATE - timedelta(days=days_ago), hour, 0),
        "note": "模拟反馈",
        "share_with_family": share,
    }


def generate() -> dict:
    cases = []

    cases.append(build_case(
        1001, "正常规律", [], False,
        base_builder(),
    ))
    cases.append(build_case(
        1002, "不同作息（晚睡晚起）", [], False,
        base_builder(checkin_hour=11, checkin_spread=30, as_of_hour=12),
    ))
    cases.append(build_case(
        1003, "偶尔漏签到", [], False,
        base_builder(skip_days=(10,)),
    ))
    cases.append(build_case(
        1004, "连续漏签到", ["R1_CHECKIN_TIME_DEVIATION", "R3_CONSECUTIVE_MISSING_CHECKINS"], False,
        base_builder(skip_days=(27, 28, 29), as_of_hour=10),
    ))
    cases.append(build_case(
        1005, "手表离线（用户已主动签到）", [], False,
        base_builder(offline_last=3),
    ))
    cases.append(build_case(
        1006, "同步延迟（今日无签到）", ["R1_CHECKIN_TIME_DEVIATION"], False,
        base_builder(pending_last=1, as_of_hour=10),
    ))
    cases.append(build_case(
        1007, "连续负面反馈且已授权分享", ["R4_CONSECUTIVE_NEGATIVE_FEEDBACK"], True,
        base_builder(extra_feedbacks=[
            feedback("feeling_unwell", 1, share=True),
            feedback("feeling_unwell", 0, share=True),
        ]),
    ))
    cases.append(build_case(
        1008, "历史数据不足", [], False,
        base_builder(history_days=3),
    ))
    cases.append(build_case(
        1009, "本人请求联系但家属未授权", ["R5_USER_REQUESTS_FAMILY_CONTACT"], False,
        base_builder(auth=authorized(active=False), extra_feedbacks=[
            feedback("want_family_contact", 0, share=True),
        ]),
    ))
    cases.append(build_case(
        1010, "活动记录骤减", ["R2_ACTIVITY_COUNT_DROP"], False,
        base_builder(activity_drop_last=6),
    ))

    for case in cases:
        case["input"]["user_id"] = case["user_id"]

    return {
        "simulated": True,
        "notice": "全部为模拟数据，仅用于算法演示与测试，不得称为真实设备采集或医疗依据",
        "generated_by": "testdata/generate_test_data.py",
        "rule_version": "1.0.0",
        "date_range": [START_DATE.date().isoformat(), LAST_DATE.date().isoformat()],
        "cases": cases,
    }


def load_cases(path: str | Path | None = None) -> list[dict]:
    path = path or Path(__file__).with_name("simulated_profiles.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["cases"]


if __name__ == "__main__":
    output = Path(__file__).with_name("simulated_profiles.json")
    payload = generate()
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 {len(payload['cases'])} 个模拟用户 -> {output}")
    for case in payload["cases"]:
        print(f"  {case['user_id']} {case['scenario']} 预期规则: {case['expected_rules']}")
