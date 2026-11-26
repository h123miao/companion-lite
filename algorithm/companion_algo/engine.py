"""统一入口：后端只需调用 analyze(dict) -> dict。

示例（成员 C 在 FastAPI 中）：
    from companion_algo import analyze
    result = analyze({
        "user_id": 1001,
        "as_of": "2026-11-26T10:00:00Z",
        "checkins": [...],
        "activities": [...],
        "health_records": [...],
        "device_states": [...],
        "feedbacks": [...],
        "authorizations": [...],
        "simulated": True,
    })
"""

from __future__ import annotations

from .baseline import compute_baseline
from .care_trigger import build_care_event
from .change_detection import detect_changes
from .credibility import assess_credibility
from .rules import DEFAULT_CONFIG, RULE_VERSION
from .schema import AnalysisInput
from .utils import iso_utc, parse_time


def analyze(data: dict | AnalysisInput, config: dict | None = None) -> dict:
    """执行一次完整分析，返回可直接 JSON 序列化的结果。"""
    inp = data if isinstance(data, AnalysisInput) else AnalysisInput.from_dict(data)
    cfg = {**DEFAULT_CONFIG, **(inp.config or {}), **(config or {})}

    baseline = compute_baseline(inp, cfg)
    credibility = assess_credibility(inp, baseline, cfg)
    changes = detect_changes(inp, baseline, credibility, cfg)
    event = build_care_event(inp, baseline, credibility, changes, cfg)

    detected_count = len(changes["detected"])
    if credibility.insufficient:
        summary = "数据不足，暂不判断生活变化"
    elif detected_count == 0:
        summary = "未发现明显生活规律变化"
    else:
        summary = (
            f"识别到 {detected_count} 条生活规律变化；"
            + ("已生成主动询问，先确认本人情况" if event and event["requires_self_confirmation"]
               else "已根据本人明确反馈生成关怀事件")
        )

    return {
        "user_id": inp.user_id,
        "analyzed_at": iso_utc(parse_time(inp.as_of)),
        "rule_version": RULE_VERSION,
        "simulated": inp.simulated,
        "data_notice": (
            "本结果基于模拟数据，仅用于演示算法流程，不代表真实设备采集或医疗判断"
            if inp.simulated else
            "本结果仅用于生活关怀参考，不构成医疗诊断或风险预测"
        ),
        "baseline": baseline.to_dict(),
        "credibility": credibility.to_dict(),
        "changes": changes,
        "care_event": event,
        "care_event_status": event["event_status"] if event else "no_change",
        "summary": summary,
    }
