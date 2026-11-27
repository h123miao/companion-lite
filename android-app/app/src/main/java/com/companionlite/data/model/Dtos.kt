package com.companionlite.data.model

import com.google.gson.annotations.SerializedName

/*
 * 传输对象（DTO）—— 和后端 JSON 一一对应，只负责"搬数据"，界面不直接用它们。
 * 界面用的是 Models.kt 里的 DailyCheckIn / ActivityRecord 等展示模型，
 * 两者的转换在 Mappers.kt 里做。
 *
 * 约定（摘自 docs/api.md）：
 *   - JSON 字段一律 snake_case；Kotlin 用驼峰，靠 @SerializedName 显式绑定。
 *     不写 @SerializedName 也能靠 Gson 猜，但后端一改名就会静默变成 null，
 *     所以这里全部显式写死。
 *   - 时间一律 ISO-8601 UTC 字符串，例 "2026-11-26T00:30:00Z"。
 *   - 列表为空时后端返回 []，不返回 null。
 *
 * ⚠️ 待确认：docs/api.md 第 3 节目前只给了接口路径和公共字段，
 *    具体的响应体结构还是草案。下面的字段是按「公共字段约定」+ A 的界面需求推出来的，
 *    需要 C 定稿后逐个核对，对不上的地方以 api.md 为准，改这里，不要改页面。
 */

// ---------------- 认证 ----------------

data class RegisterRequest(
    val username: String,
    val password: String,
    @SerializedName("display_name") val displayName: String,
    val role: String,                    // elder / family
    val phone: String? = null
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String = "Bearer",
    val user: UserDto
)

data class UserDto(
    val id: Int,
    val username: String = "",
    @SerializedName("display_name") val displayName: String = "",
    val role: String = "elder",           // elder / family
    val phone: String? = null,
    @SerializedName("invite_code") val inviteCode: String? = null
)

// ---------------- 家庭关系 ----------------

data class InviteCodeDto(
    @SerializedName("invite_code") val inviteCode: String,
    @SerializedName("expires_at") val expiresAt: String? = null
)

data class BindRequest(
    @SerializedName("invite_code") val inviteCode: String,
    val relation: String? = null          // 女儿 / 儿子 / 其他
)

data class FamilyLinkDto(
    val id: Int,
    @SerializedName("elder_id") val elderId: Int,
    @SerializedName("family_id") val familyId: Int,
    val status: String = "pending",       // pending / active / revoked
    @SerializedName("elder_name") val elderName: String? = null,
    @SerializedName("family_name") val familyName: String? = null,
    val relation: String? = null,
    @SerializedName("can_view_status") val canViewStatus: Boolean = false,
    @SerializedName("can_view_activity") val canViewActivity: Boolean = false,
    @SerializedName("can_view_feedback") val canViewFeedback: Boolean = false,
    @SerializedName("can_receive_alerts") val canReceiveAlerts: Boolean = false
)

/** 修改授权范围 / 撤销授权都用它，只传要改的字段 */
data class FamilyLinkUpdateRequest(
    val status: String? = null,           // 撤销授权时传 revoked
    @SerializedName("can_view_status") val canViewStatus: Boolean? = null,
    @SerializedName("can_view_activity") val canViewActivity: Boolean? = null,
    @SerializedName("can_view_feedback") val canViewFeedback: Boolean? = null,
    @SerializedName("can_receive_alerts") val canReceiveAlerts: Boolean? = null
)

// ---------------- 生活记录 ----------------

data class CheckInRequest(
    val status: String,                   // good / normal / unwell / need_help
    val mood: String? = null,             // happy / calm / tired / low
    val note: String? = null,
    @SerializedName("want_family_call") val wantFamilyCall: Boolean = false,
    @SerializedName("data_source") val dataSource: String = "manual"
)

data class CheckInDto(
    val id: Int = 0,
    @SerializedName("user_id") val userId: Int = 0,
    @SerializedName("check_in_at") val checkInAt: String,
    val status: String = "normal",
    val mood: String? = null,
    val note: String? = null,
    @SerializedName("want_family_call") val wantFamilyCall: Boolean = false,
    @SerializedName("data_source") val dataSource: String = "manual",
    @SerializedName("sync_status") val syncStatus: String = "synced",
    /** 数据可信度：界面必须拿到它，不允许在客户端猜 */
    @SerializedName("trust_state") val trustState: String = "normal"
)

data class ActivityRequest(
    @SerializedName("activity_type") val activityType: String,
    @SerializedName("recorded_at") val recordedAt: String? = null,
    val note: String? = null,
    @SerializedName("data_source") val dataSource: String = "manual"
)

data class ActivityDto(
    val id: Int = 0,
    @SerializedName("user_id") val userId: Int = 0,
    @SerializedName("activity_type") val activityType: String,
    @SerializedName("recorded_at") val recordedAt: String,
    val note: String? = null,
    @SerializedName("data_source") val dataSource: String = "manual",
    @SerializedName("sync_status") val syncStatus: String = "synced",
    @SerializedName("trust_state") val trustState: String = "normal"
)

// ---------------- 分析与关怀 ----------------

data class BaselineDto(
    @SerializedName("user_id") val userId: Int = 0,
    @SerializedName("window_days") val windowDays: Int = 14,
    @SerializedName("valid_days") val validDays: Int = 0,
    /** 样本不够时后端返回 false，界面显示「数据不足，暂不判断」 */
    @SerializedName("sample_sufficient") val sampleSufficient: Boolean = false,
    @SerializedName("checkin_median") val checkinMedian: String? = null,   // "07:52"
    @SerializedName("checkin_earliest") val checkinEarliest: String? = null,
    @SerializedName("checkin_latest") val checkinLatest: String? = null,
    @SerializedName("spread_minutes") val spreadMinutes: Int = 0,
    @SerializedName("activity_daily_mean") val activityDailyMean: Double = 0.0,
    @SerializedName("trust_state") val trustState: String = "insufficient"
)

data class CareEventDto(
    val id: Int,
    @SerializedName("user_id") val userId: Int = 0,
    @SerializedName("trigger_rule") val triggerRule: String = "",
    /** 系统想对本人说的话，例如"今天还没有收到你的签到记录……" */
    @SerializedName("inquiry_text") val inquiryText: String = "",
    @SerializedName("created_at") val createdAt: String = "",
    @SerializedName("event_status") val eventStatus: String = "pending",
    @SerializedName("trust_state") val trustState: String = "normal"
)

data class FeedbackRequest(
    /** i_am_fine / busy / unwell / want_call / no_answer */
    @SerializedName("feedback_type") val feedbackType: String
)

data class EventStatusRequest(
    /** awaiting_family / handled / closed */
    @SerializedName("event_status") val eventStatus: String
)
