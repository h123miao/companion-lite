"""规则阈值集中管理。

所有阈值放在这里，答辩时可以逐条解释"为什么这样设"，也方便赛前调参。
任何规则都不允许输出"用户发生危险/需要急救"这类医疗结论。
"""

RULE_VERSION = "1.0.0"

DEFAULT_CONFIG: dict = {
    # 个人生活基线
    "baseline_window_days": 14,        # 取最近 14 天建立个人规律
    "baseline_min_days": 7,            # 至少 7 天有效记录，否则输出"数据不足"
    "timezone_offset_hours": 8.0,      # 北京时间 UTC+8
    # 规则一：签到时间偏离
    "checkin_window_iqr_scale": 0.5,   # 典型签到区间 = [Q1-0.5*IQR, Q3+0.5*IQR]
    "checkin_min_window_minutes": 60,  # 典型区间至少 1 小时，避免过窄误报
    "checkin_grace_minutes": 30,       # 超过典型区间末端 30 分钟才提示
    # 规则二：活动记录变化
    "activity_recent_days": 3,         # 用最近 3 个完整天对比基线
    "activity_drop_ratio": 0.4,        # 活动量 <= 基线的 40% 视为明显下降
    "activity_min_baseline": 1.0,      # 基线活动量太低时不判断
    # 规则三：连续漏签到
    "consecutive_missing_days": 2,     # 连续 2 个完整天无签到（不含今天）
    # 规则四：连续负面反馈
    "consecutive_negative_feedback": 2,
}

NEGATIVE_FEEDBACK_TYPES = {"feeling_unwell", "need_help"}
CONTACT_REQUEST_FEEDBACK = "want_family_contact"

RULE_META: dict[str, dict[str, str]] = {
    "R1_CHECKIN_TIME_DEVIATION": {
        "name": "签到时间偏离",
        "description": "本人历史签到时间集中在某个区间，当前已明显超出该区间且仍未签到。",
    },
    "R2_ACTIVITY_COUNT_DROP": {
        "name": "活动记录数量下降",
        "description": "最近几天的活动记录数量明显低于本人历史平均水平。",
    },
    "R3_CONSECUTIVE_MISSING_CHECKINS": {
        "name": "连续漏签到",
        "description": "连续多个完整自然日没有收到签到记录。",
    },
    "R4_CONSECUTIVE_NEGATIVE_FEEDBACK": {
        "name": "连续负面反馈",
        "description": "本人连续多次主动反馈身体不适或需要帮助。",
    },
    "R5_USER_REQUESTS_FAMILY_CONTACT": {
        "name": "本人请求家人联系",
        "description": "本人明确选择'希望家人联系我'，这是主动表达，不是系统推断。",
    },
}
