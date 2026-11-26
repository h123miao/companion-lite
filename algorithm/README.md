# algorithm / —— 成员 D 的算法目录

> 负责人：**成员 D** ｜ 其他人不要改这个目录

## 这里放什么

```text
algorithm/
├── requirements.txt
├── pytest.ini
├── companion_algorithm/            # 独立的 Python 包，后端直接 import
│   ├── __init__.py
│   ├── baseline.py                 # 个人生活基线：中位数、波动、有效天数
│   ├── trust.py                    # 数据可信度：6 种状态的判定
│   ├── change_detection.py         # 生活变化识别：签到偏离 / 活动减少 / 反馈异常
│   └── care.py                     # 主动关怀触发与事件生成
└── tests/                          # pytest 用例
```

## 输入输出约定（与 C 对齐）

输入统一用 dict 或 DataFrame，字段与 `docs/api.md` 一致：

```python
{
    "user_id": 1001,
    "check_ins": [{"check_in_at": "2026-11-26T00:30:00Z", "trust_state": "user_feedback"}, ...],
    "activities": [{"recorded_at": "2026-11-26T01:10:00Z", "activity_type": "meal"}, ...]
}
```

输出必须能直接给 Android 用：

```python
{
    "valid_days": 11,
    "median_check_in": "07:52",
    "spread_minutes": 40,
    "trust_state": "normal",          # insufficient 时界面显示"数据不足，暂不判断"
    "events": [
        {"trigger_rule": "signin_deviation",
         "reason": "今天 10:30 还没有收到签到记录",
         "trust_state": "missing"}
    ]
}
```

## 必须遵守

1. 有效记录不足时返回 `trust_state = "insufficient"`，**不允许**输出"异常"。
2. 每条事件必须能解释：用了什么数据、命中哪条规则、为什么触发。
3. 不引入深度学习模型，先用统计 + 规则，保证能讲清楚。
4. 不声称模拟数据证明了真实的医疗风险预测能力。

## 测试

```bash
cd algorithm
pytest -q
```

## 当前状态

⏳ 等待 D 提交基线算法与第一版测试。
