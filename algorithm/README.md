# 伴行·时序 —— 成员 D 算法模块

**职责**：个人生活基线、数据可信度判断、生活变化识别、主动关怀触发、模拟测试数据与测试报告。
**边界**：本模块是独立的 Python 包，不访问数据库、不依赖 Android、不依赖 FastAPI。后端把数据整理成 dict 传入，拿回 dict。

> 核心算法只用 Python 标准库，队友机器上不需要额外安装 numpy / pandas 就能跑。
> 这样是为了降低合并时的环境冲突；如团队统一要求，可自行在 `requirements.txt` 中启用。

---

## 一、目录结构

```
algorithm/
├── companion_algo/            # 算法包（提交到 feature/algorithm 分支）
│   ├── __init__.py            # 对外只暴露 analyze / apply_feedback / complete_event
│   ├── schema.py              # 输入数据结构，字段名与团队约定一致
│   ├── rules.py               # 所有规则阈值集中管理，方便答辩解释和调参
│   ├── utils.py               # ISO 时间解析、UTC+8 换算、分位数
│   ├── baseline.py            # 核心算法一：个人生活基线
│   ├── credibility.py         # 核心算法二：数据可信度
│   ├── change_detection.py    # 核心算法三：生活变化识别（5 条规则）
│   ├── care_trigger.py        # 核心算法四：主动关怀触发与状态流转
│   └── engine.py              # 统一入口 analyze()
├── testdata/
│   ├── generate_test_data.py  # 生成 10 用户 × 30 天模拟数据
│   └── simulated_profiles.json
├── tests/                     # 24 项 pytest 测试
├── report/test_report.md      # 实际运行生成的测试报告
├── evaluate.py                # 场景评估 + 生成报告
└── requirements.txt
```

## 二、快速开始

```bash
cd algorithm
python -m pip install -r requirements.txt      # 只需 pytest
python testdata/generate_test_data.py          # 生成模拟数据（可复现）
python -m pytest tests -q                      # 运行单元测试
python evaluate.py                             # 生成 report/test_report.md
```

预期输出：`24 passed`，评估报告 `TP=6 FP=0 FN=0 Precision=100.00% Recall=100.00%`。

## 三、给成员 C：输入契约

后端从数据库查出数据后，组装成下面这个 dict 调用：

```python
from companion_algo import analyze

result = analyze({
    "user_id": 1001,
    "as_of": "2026-11-26T02:00:00Z",       # 分析基准时刻，UTC
    "simulated": True,                     # 模拟数据必须标 True
    "checkins": [{
        "check_in_at": "2026-11-26T00:15:00Z",
        "mood": "good", "status": "normal", "note": "",
        "data_source": "manual", "sync_status": "synced", "confirmed": True
    }],
    "activities": [{
        "activity_type": "外出", "recorded_at": "2026-11-26T02:00:00Z",
        "note": "", "data_source": "manual", "sync_status": "synced"
    }],
    "health_records": [{
        "metric": "steps", "value": 3200,
        "collected_at": "2026-11-25T13:00:00Z",
        "uploaded_at": "2026-11-25T13:05:00Z",
        "data_source": "simulated_watch", "valid": True, "sync_status": "synced"
    }],
    "device_states": [{
        "device_id": "sim_watch_01", "is_online": True,
        "last_seen_at": "2026-11-26T00:00:00Z",
        "data_source": "simulated_watch"
    }],
    "feedbacks": [{
        "feedback_type": "feeling_good",
        "created_at": "2026-11-26T01:00:00Z",
        "note": "", "share_with_family": False
    }],
    "authorizations": [{
        "family_user_id": 2001, "status": "active",
        "scope": ["status", "care_events"], "can_receive_alerts": True
    }]
})
```

字段约定（沿用团队统一命名，不要改）：

| 数据 | 字段 | 说明 |
| --- | --- | --- |
| 用户编号 | `user_id` | int |
| 签到时间 | `check_in_at` | ISO 8601 UTC，Z 结尾 |
| 活动类型 | `activity_type` | 起床/外出/回家/用餐/运动/休息/服药/其他 |
| 活动时间 | `recorded_at` | ISO 8601 UTC |
| 数据来源 | `data_source` | `manual` / `watch` / `simulated_watch` |
| 同步状态 | `sync_status` | `synced` / `pending` / `failed` |
| 反馈类型 | `feedback_type` | 见下表 |
| 关怀事件状态 | `event_status` | 算法输出在 `care_event.event_status` |
| 授权 | `authorizations` | `status`、`scope`、`can_receive_alerts` 缺一不可 |

反馈类型合法值：`feeling_good`、`busy_today`、`feeling_unwell`、`need_help`、`want_family_contact`、`declined_to_answer`。

## 四、给成员 C / B：输出契约

`analyze()` 返回纯 dict，可直接 `JSONResponse(content=result)` 或存进 `care_events` 表：

| 字段 | 含义 |
| --- | --- |
| `baseline` | 个人基线：签到中位数、典型时间窗、活动均值、覆盖天数；`sufficient=false` 时附 `insufficient_reason` |
| `credibility` | 可信度：`overall_status` 六种状态之一，`reasons` 是逐条解释，`insufficient` 为独立阻断标志 |
| `changes.detected` | 命中的规则列表，每条含 `rule_id`、`reason`、`data_used`、`data_status`、`confidence` |
| `changes.suppressed` | 被抑制的规则及原因（例如数据不足） |
| `care_event` | 关怀事件；无变化时为 `null` |
| `care_event_status` | `no_change` / `pending_self_confirmation` / `pending_family_action` / `pending_authorization` / `resolved_self_ok` / `awaiting_recheck` / `completed` |
| `summary` | 一句话摘要，可直接显示在家属端 |
| `data_notice` | 模拟数据或医疗边界声明，展示层必须显示 |

`care_event` 里的关键字段：`event_type`、`inquiry_text`（主动询问文案）、`options`（5 个选项）、`requires_self_confirmation`、`notify_family`、`notify_family_reason`、`authorized_family_ids`。

本人提交反馈后，把当前 `care_event` 传回更新状态：

```python
from companion_algo import apply_feedback, complete_event
updated = apply_feedback(event, "want_family_contact", input_dict)   # dict 或 AnalysisInput 均可
done = complete_event(updated)   # 家属完成联系后
```

后端必须二次校验授权：算法给出的 `authorized_family_ids` 只是建议，**最终权限判断在后端做**。

## 五、五条规则（答辩可直接照着讲）

| 规则 | 触发条件 | 阈值位置 |
| --- | --- | --- |
| R1 签到时间偏离 | 今天未签到且已过个人典型时间窗 +30 分钟；或今天签到明显偏晚 | `checkin_grace_minutes` |
| R2 活动记录下降 | 最近 3 个完整日活动量 ≤ 个人基线的 40% | `activity_drop_ratio` |
| R3 连续漏签到 | 连续 2 个完整自然日无签到（不含今天） | `consecutive_missing_days` |
| R4 连续负面反馈 | 本人连续 2 次反馈不适或需要帮助 | `consecutive_negative_feedback` |
| R5 请求家人联系 | 本人明确选择"希望家人联系我" | — |

**硬性安全规则**：
- 数据缺失 / 设备离线 / 同步延迟 → 只标记 `missing_unknown` / `device_offline` / `sync_delay`，绝不输出危险结论。
- 历史少于 7 天 → 输出"数据不足，暂不判断"，五条规则全部抑制。
- R1—R3 只生成本人询问，`notify_family=false`。
- 只有本人明确反馈 + 有效授权，才允许 `notify_family=true`。

## 六、常见问题

1. **`ModuleNotFoundError: companion_algo`**：先 `cd algorithm` 再运行，或设置 `PYTHONPATH=algorithm`。
2. **想改阈值**：只改 `companion_algo/rules.py` 的 `DEFAULT_CONFIG`，然后重新运行 `evaluate.py` 更新报告。
3. **模拟数据被当成真实数据**：所有模拟用例都有 `simulated=true`，`data_notice` 会输出声明；Android 展示层必须显示该声明。
4. **合并冲突**：本模块只写 `algorithm/`，不会碰 A/B/C 的文件。分支名 `feature/algorithm`。
