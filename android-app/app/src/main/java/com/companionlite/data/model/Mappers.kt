package com.companionlite.data.model

import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

/**
 * DTO ←→ 界面模型的转换。
 *
 * 两条铁律：
 * 1. **转换函数永远不抛异常**。后端哪天多返回个 null、时间格式不对，
 *    顶多是"这一条显示不出来"，不能让整个页面崩掉。
 * 2. **不认识的状态一律按"数据缺失"处理**，不许当成"正常"，更不许当成"危险"。
 *    这是项目定位决定的：没有信息的时候，系统只能说"不清楚"。
 */
object Mappers {

    private val TIME_TEXT = DateTimeFormatter.ofPattern("HH:mm")
    private val DATE_TEXT = DateTimeFormatter.ofPattern("M月d日")

    // ---------------- 时间 ----------------

    /** "2026-11-26T00:30:00Z" / "2026-11-26T08:30:00+08:00" → 本机时区的时刻 */
    private fun parseZoned(text: String?): ZonedDateTime? {
        if (text.isNullOrBlank()) return null
        return try {
            OffsetDateTime.parse(text).atZoneSameInstant(ZoneId.systemDefault())
        } catch (_: Exception) {
            try {
                Instant.parse(text).atZone(ZoneId.systemDefault())
            } catch (_: Exception) {
                null
            }
        }
    }

    /** "07:52" / "07:52:00" → LocalTime，失败返回 null */
    private fun parseLocalTime(text: String?): LocalTime? {
        if (text.isNullOrBlank()) return null
        return try {
            LocalTime.parse(text.take(8))
        } catch (_: Exception) {
            null
        }
    }

    /** 关怀事件列表里显示成"今天 10:30"，比一整串 ISO 时间好读 */
    private fun dayTimeText(zoned: ZonedDateTime?): String {
        if (zoned == null) return ""
        val date = zoned.toLocalDate()
        val today = LocalDate.now()
        val time = zoned.toLocalTime().format(TIME_TEXT)
        return when (date) {
            today -> "今天 $time"
            today.minusDays(1) -> "昨天 $time"
            else -> "${date.format(DATE_TEXT)} $time"
        }
    }

    // ---------------- 状态字符串 → A 的展示枚举 ----------------

    /**
     * trust_state。api.md 定义了 6 种；后端若返回了没见过的值，
     * 我们既不能说"正常"，也不能说"有危险"，只能老老实实说"原因未知"。
     */
    fun trustState(raw: String?): DataTrustState = when (raw?.lowercase()) {
        "normal" -> DataTrustState.NORMAL
        "missing" -> DataTrustState.MISSING
        "offline" -> DataTrustState.OFFLINE
        "delayed" -> DataTrustState.DELAYED
        "user_feedback" -> DataTrustState.USER_FEEDBACK
        "insufficient" -> DataTrustState.INSUFFICIENT
        else -> DataTrustState.MISSING
    }

    fun checkInStatus(raw: String?): CheckInStatus = when (raw?.lowercase()) {
        "good" -> CheckInStatus.GOOD
        "unwell" -> CheckInStatus.UNWELL
        "need_help" -> CheckInStatus.NEED_HELP
        else -> CheckInStatus.NORMAL
    }

    fun checkInStatusToWire(status: CheckInStatus): String = when (status) {
        CheckInStatus.GOOD -> "good"
        CheckInStatus.NORMAL -> "normal"
        CheckInStatus.UNWELL -> "unwell"
        CheckInStatus.NEED_HELP -> "need_help"
    }

    fun mood(raw: String?): MoodType? = when (raw?.lowercase()) {
        "happy", "good" -> MoodType.HAPPY
        "calm", "normal" -> MoodType.CALM
        "tired" -> MoodType.TIRED
        "low", "bad" -> MoodType.LOW
        else -> null
    }

    fun moodToWire(mood: MoodType?): String? = when (mood) {
        MoodType.HAPPY -> "happy"
        MoodType.CALM -> "calm"
        MoodType.TIRED -> "tired"
        MoodType.LOW -> "low"
        else -> null
    }

    fun activityType(raw: String?): ActivityType = when (raw?.lowercase()) {
        "wake" -> ActivityType.WAKE
        "out" -> ActivityType.OUT
        "home" -> ActivityType.HOME
        "meal" -> ActivityType.MEAL
        "exercise" -> ActivityType.EXERCISE
        "rest" -> ActivityType.REST
        "medicine" -> ActivityType.MEDICINE
        else -> ActivityType.OTHER
    }

    fun activityTypeToWire(type: ActivityType): String = when (type) {
        ActivityType.WAKE -> "wake"
        ActivityType.OUT -> "out"
        ActivityType.HOME -> "home"
        ActivityType.MEAL -> "meal"
        ActivityType.EXERCISE -> "exercise"
        ActivityType.REST -> "rest"
        ActivityType.MEDICINE -> "medicine"
        ActivityType.OTHER -> "other"
    }

    fun careEventStatus(raw: String?): CareEventStatus = when (raw?.lowercase()) {
        "pending" -> CareEventStatus.PENDING
        "awaiting_family" -> CareEventStatus.AWAITING_FAMILY
        "handled" -> CareEventStatus.HANDLED
        "closed" -> CareEventStatus.CLOSED
        else -> CareEventStatus.PENDING
    }

    fun feedbackType(raw: String?): FeedbackType = when (raw?.lowercase()) {
        "i_am_fine" -> FeedbackType.I_AM_FINE
        "busy" -> FeedbackType.BUSY
        "unwell" -> FeedbackType.UNWELL
        "want_call" -> FeedbackType.WANT_CALL
        "no_answer" -> FeedbackType.NO_ANSWER
        else -> FeedbackType.NO_ANSWER
    }

    fun feedbackTypeToWire(feedback: FeedbackType): String = when (feedback) {
        FeedbackType.I_AM_FINE -> "i_am_fine"
        FeedbackType.BUSY -> "busy"
        FeedbackType.UNWELL -> "unwell"
        FeedbackType.WANT_CALL -> "want_call"
        FeedbackType.NO_ANSWER -> "no_answer"
    }

    // ---------------- DTO → 界面模型 ----------------

    fun toDailyCheckIn(dto: CheckInDto): DailyCheckIn? {
        val zoned = parseZoned(dto.checkInAt) ?: return null
        return DailyCheckIn(
            date = zoned.toLocalDate(),
            time = zoned.toLocalTime(),
            status = checkInStatus(dto.status),
            mood = mood(dto.mood),
            note = dto.note.orEmpty(),
            trust = trustState(dto.trustState)
        )
    }

    fun toActivityRecord(dto: ActivityDto): ActivityRecord? {
        val zoned = parseZoned(dto.recordedAt) ?: return null
        return ActivityRecord(
            id = dto.id.toLong(),
            type = activityType(dto.activityType),
            date = zoned.toLocalDate(),
            time = zoned.toLocalTime(),
            note = dto.note.orEmpty(),
            source = when (dto.dataSource) {
                "watch" -> "手表采集"
                "phone" -> "手机自动记录"
                else -> "本人记录"
            },
            trust = trustState(dto.trustState)
        )
    }

    fun toBaseline(dto: BaselineDto): BaselineProfile = BaselineProfile(
        validDays = dto.validDays,
        medianCheckIn = parseLocalTime(dto.checkinMedian),
        earliest = parseLocalTime(dto.checkinEarliest),
        latest = parseLocalTime(dto.checkinLatest),
        spreadMinutes = dto.spreadMinutes,
        dailyActivityAvg = dto.activityDailyMean,
        // 样本不足时必须显示"数据不足，暂不判断"，不能被后端的 trust_state 盖过去
        trust = if (!dto.sampleSufficient) {
            DataTrustState.INSUFFICIENT
        } else {
            trustState(dto.trustState)
        }
    )

    fun toCareEvent(dto: CareEventDto): CareEvent = CareEvent(
        id = dto.id.toLong(),
        triggerRule = dto.triggerRule,
        reason = dto.inquiryText,
        createdAtText = dayTimeText(parseZoned(dto.createdAt)),
        status = careEventStatus(dto.eventStatus),
        trust = trustState(dto.trustState)
    )

    fun toFamilyMember(dto: FamilyLinkDto): FamilyMember = FamilyMember(
        name = dto.familyName ?: dto.elderName.orEmpty(),
        relation = dto.relation ?: "家属",
        canViewStatus = dto.canViewStatus,
        canReceiveAlert = dto.canReceiveAlerts
    )

    fun toUserProfile(dto: UserDto): UserProfile = UserProfile(
        userId = dto.id.toLong(),
        name = dto.displayName.ifBlank { dto.username },
        roleLabel = if (dto.role == "family") "家属" else "本人",
        phone = dto.phone.orEmpty(),
        inviteCode = dto.inviteCode.orEmpty()
    )
}
