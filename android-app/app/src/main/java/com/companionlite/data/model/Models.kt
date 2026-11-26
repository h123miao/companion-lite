package com.companionlite.data.model

import java.time.LocalDate
import java.time.LocalTime

/*
 * 数据模型（成员 A 的 UI 层用；成员 B 接入后端时以这份字段为准扩展）
 *
 * 字段命名必须和 docs/api.md 的「公共字段约定」一致：
 *   user_id / check_in_at / activity_type / recorded_at / data_source
 *   sync_status / feedback_type / event_status
 * Kotlin 里驼峰，JSON 里下划线，由成员 B 在 Retrofit 的 Converter 里统一转换，
 * 页面代码不要自己拼 JSON 字段名。
 */

/**
 * 数据可信度状态：本项目创新点之一。
 * UI 必须能把「没收到数据」和「用户真的没活动」区分开，
 * 任何一屏都不允许把 MISSING / OFFLINE / DELAYED 显示成"异常"或"危险"。
 */
enum class DataTrustState(val label: String, val explanation: String) {
    NORMAL("正常记录", "已收到完整数据"),
    MISSING("数据缺失", "还没有收到这段时间的数据，原因未知"),
    OFFLINE("设备离线", "手机或手表处于离线状态"),
    DELAYED("同步延迟", "数据还没有同步完成"),
    USER_FEEDBACK("本人反馈", "由本人主动填写"),
    INSUFFICIENT("数据不足", "历史记录太少，暂不判断")
}

/** 签到时的主观状态 */
enum class CheckInStatus(val label: String) {
    GOOD("很好"),
    NORMAL("一般"),
    UNWELL("有些不舒服"),
    NEED_HELP("需要帮助")
}

/** 心情 */
enum class MoodType(val label: String) {
    HAPPY("开心"),
    CALM("平静"),
    TIRED("有点累"),
    LOW("不太好"),
    UNKNOWN("未选择")
}

/** 活动类型，与后端 activity_type 枚举保持一致 */
enum class ActivityType(val label: String) {
    WAKE("起床"),
    OUT("外出"),
    HOME("回家"),
    MEAL("用餐"),
    EXERCISE("运动"),
    REST("休息"),
    MEDICINE("服药"),
    OTHER("其他")
}

/** 收到主动询问后，本人的反馈（feedback_type） */
enum class FeedbackType(val label: String) {
    I_AM_FINE("我很好"),
    BUSY("今天比较忙"),
    UNWELL("今天不太舒服"),
    WANT_CALL("希望家人联系我"),
    NO_ANSWER("暂时不想回答")
}

/** 关怀事件状态（event_status） */
enum class CareEventStatus(val label: String) {
    PENDING("待本人确认"),
    AWAITING_FAMILY("等待家属处理"),
    HANDLED("已处理"),
    CLOSED("已关闭")
}

/** 一天一条签到记录 */
data class DailyCheckIn(
    val date: LocalDate,
    val time: LocalTime?,
    val status: CheckInStatus?,
    val mood: MoodType?,
    val note: String = "",
    val trust: DataTrustState = DataTrustState.USER_FEEDBACK
)

/** 一条活动记录 */
data class ActivityRecord(
    val id: Long,
    val type: ActivityType,
    val date: LocalDate,
    val time: LocalTime,
    val note: String = "",
    val source: String = "本人记录",
    val trust: DataTrustState = DataTrustState.USER_FEEDBACK
)

/**
 * 个人生活基线：数值由成员 D 的算法（algorithm/）计算后经后端返回，
 * UI 只负责展示，不在客户端重新计算。
 */
data class BaselineProfile(
    val validDays: Int,
    val medianCheckIn: LocalTime?,
    val earliest: LocalTime?,
    val latest: LocalTime?,
    val spreadMinutes: Int,
    val dailyActivityAvg: Double,
    val trust: DataTrustState
)

/** 关怀事件：识别 + 询问 + 家属协同的载体 */
data class CareEvent(
    val id: Long,
    val triggerRule: String,
    val reason: String,
    val createdAtText: String,
    val status: CareEventStatus,
    val trust: DataTrustState
)

/** 已绑定的家属 */
data class FamilyMember(
    val name: String,
    val relation: String,
    val canViewStatus: Boolean,
    val canReceiveAlert: Boolean
)

/** 本人资料 */
data class UserProfile(
    val userId: Long,
    val name: String,
    val roleLabel: String,
    val phone: String,
    val inviteCode: String
)
