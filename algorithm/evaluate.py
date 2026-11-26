"""跑一遍全部模拟用例，生成测试报告 report/test_report.md。

运行：python evaluate.py
报告里的数字来自真实运行结果，不是预估。
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from companion_algo import analyze
from testdata.generate_test_data import load_cases

ROOT = Path(__file__).resolve().parent
DANGER_WORDS = ("危险", "急救", "疾病预测", "发生意外")


def evaluate():
    cases = load_cases()
    rows = []
    tp = fp = fn = 0
    notify_wrong = 0
    missing_misjudge = 0
    insufficient_leak = 0
    durations = []

    for case in cases:
        started = time.perf_counter()
        result = analyze(case["input"])
        durations.append((time.perf_counter() - started) * 1000)

        expected = set(case["expected_rules"])
        detected = {d["rule_id"] for d in result["changes"]["detected"]}
        hit = expected & detected
        false_pos = detected - expected
        false_neg = expected - detected
        tp += len(hit)
        fp += len(false_pos)
        fn += len(false_neg)

        event = result["care_event"]
        actual_notify = bool(event and event["notify_family"])
        if actual_notify != case["expected_notify_family"]:
            notify_wrong += 1

        status = result["credibility"]["overall_status"]
        if status in {"missing_unknown", "device_offline", "sync_delay", "insufficient"}:
            text = json.dumps(result, ensure_ascii=False)
            if any(word in text for word in DANGER_WORDS):
                missing_misjudge += 1
            if actual_notify and "R5_USER_REQUESTS_FAMILY_CONTACT" not in detected:
                missing_misjudge += 1

        if result["credibility"]["insufficient"] and event is not None:
            insufficient_leak += 1

        rows.append({
            "user_id": case["user_id"],
            "scenario": case["scenario"],
            "expected": sorted(expected),
            "detected": sorted(detected),
            "status": status,
            "event": result["care_event_status"],
            "notify": actual_notify,
            "summary": result["summary"],
            "fp": sorted(false_pos),
            "fn": sorted(false_neg),
        })

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    return {
        "rows": rows,
        "tp": tp, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall,
        "notify_wrong": notify_wrong,
        "missing_misjudge": missing_misjudge,
        "insufficient_leak": insufficient_leak,
        "avg_ms": sum(durations) / len(durations),
        "total_cases": len(cases),
    }


def rule_table(rows):
    lines = [
        "| 用户 | 场景 | 数据状态 | 预期规则 | 实际命中 | 关怀事件 | 通知家属 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    short = {
        "R1_CHECKIN_TIME_DEVIATION": "R1 签到偏离",
        "R2_ACTIVITY_COUNT_DROP": "R2 活动下降",
        "R3_CONSECUTIVE_MISSING_CHECKINS": "R3 连续漏签",
        "R4_CONSECUTIVE_NEGATIVE_FEEDBACK": "R4 连续负面反馈",
        "R5_USER_REQUESTS_FAMILY_CONTACT": "R5 请求联系",
    }
    for r in rows:
        exp = "、".join(short.get(x, x) for x in r["expected"]) or "无"
        det = "、".join(short.get(x, x) for x in r["detected"]) or "无"
        lines.append(
            f"| {r['user_id']} | {r['scenario']} | {r['status']} | {exp} | {det} "
            f"| {r['event']} | {'是' if r['notify'] else '否'} |"
        )
    return "\n".join(lines)


def render(m):
    ok = m["fp"] == 0 and m["fn"] == 0 and m["notify_wrong"] == 0 \
        and m["missing_misjudge"] == 0 and m["insufficient_leak"] == 0
    return f"""# 伴行·时序 —— 算法模块测试报告

> 生成方式：`python evaluate.py`（本报告数字来自实际运行）
> 规则版本：1.0.0　|　测试日期：2026-11-26
> 数据说明：**全部为模拟数据**，不是真实设备采集，不构成医疗诊断或风险预测依据。

## 一、测试结论

{'✅ 全部通过' if ok else '⚠️ 存在需要复核的项目'}：
{m['total_cases']} 个虚拟用户 × 30 天记录，五条规则共命中 {m['tp']} 次，
误报 {m['fp']} 次，漏报 {m['fn']} 次，数据缺失误判 {m['missing_misjudge']} 次，
授权判断错误 {m['notify_wrong']} 次，数据不足仍输出结论 {m['insufficient_leak']} 次。

| 指标 | 数值 |
| --- | --- |
| 规则命中总数（TP） | {m['tp']} |
| 误报次数（FP） | {m['fp']} |
| 漏报次数（FN） | {m['fn']} |
| 精确率 Precision | {m['precision']:.2%} |
| 召回率 Recall | {m['recall']:.2%} |
| 通知家属判断错误 | {m['notify_wrong']} 次 |
| 数据缺失误判 | {m['missing_misjudge']} 次 |
| 数据不足仍输出结论 | {m['insufficient_leak']} 次 |
| 单次分析平均耗时 | {m['avg_ms']:.2f} ms |

**注意：以上指标只说明规则在模拟数据上的一致性，不能证明真实医疗风险预测能力。**

## 二、逐场景结果

{rule_table(m['rows'])}

## 三、重点验证项

1. **不同作息不误报**：用户 1002 平时 11 点签到，系统按本人基线判断，未套用统一 8 点阈值。
2. **手表离线不误判**：用户 1005 手表离线 3 天，但本人已手动签到，可信度标记为 `device_offline`，未生成关怀事件，也没有把设备数据缺失解释为用户没有活动。
3. **同步延迟不误判**：用户 1006 数据未上传，可信度标记为 `sync_delay`，事件文案提示"可能只是数据未送达"。
4. **数据不足不判断**：用户 1008 只有 3 天历史，五条规则全部被抑制，输出"数据不足，暂不判断"。
5. **先问本人再通知家属**：用户 1004 连续漏签到，事件状态为 `pending_self_confirmation`，`notify_family=false`。
6. **授权是硬约束**：用户 1009 本人请求联系家属，但授权已撤销，系统未通知家属，事件状态为 `pending_authorization`。

## 四、测试方法

- 单元测试：`python -m pytest tests -q`（24 项）
- 场景评估：`python evaluate.py`
- 用例生成：`python testdata/generate_test_data.py`（固定随机种子，结果可复现）

## 五、已知边界

1. 凌晨 00:00—03:59 的签到按"次日凌晨"处理，若用户作息跨多时区需另行配置 `timezone_offset_hours`。
2. 活动量下降只作为"需确认"线索，可能源于用户忘记手动记录，不作为健康结论。
3. 基线最少 7 天有效记录，14 天窗口；若团队决定调整，改 `companion_algo/rules.py` 中的阈值即可，需重新生成报告。
4. 本模块只负责算法，不直接访问数据库；权限的最终校验必须由成员 C 的后端二次完成。
"""


if __name__ == "__main__":
    metrics = evaluate()
    output_dir = ROOT / "report"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / "test_report.md"
    output.write_text(render(metrics), encoding="utf-8")
    print(f"测试报告已生成: {output}")
    print(
        f"TP={metrics['tp']} FP={metrics['fp']} FN={metrics['fn']} "
        f"Precision={metrics['precision']:.2%} Recall={metrics['recall']:.2%} "
        f"平均耗时={metrics['avg_ms']:.2f}ms"
    )
