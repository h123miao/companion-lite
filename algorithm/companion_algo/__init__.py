"""伴行·时序（Companion Lite）算法模块。

职责：个人生活基线、数据可信度、生活变化识别、主动关怀触发。
本模块不依赖后端框架，后端只需传入一个 dict，拿回一个 dict。
"""

from .care_trigger import apply_feedback, complete_event
from .engine import analyze

__all__ = ["analyze", "apply_feedback", "complete_event"]
__version__ = "1.0.0"
