package com.companionlite.data.repository

import com.companionlite.data.UiState
import com.companionlite.data.mock.MockRepository
import com.companionlite.data.model.ActivityRecord
import com.companionlite.data.model.ActivityType
import com.companionlite.data.model.BaselineProfile
import com.companionlite.data.model.CareEvent
import com.companionlite.data.model.CareEventStatus
import com.companionlite.data.model.CheckInStatus
import com.companionlite.data.model.DailyCheckIn
import com.companionlite.data.model.FamilyMember
import com.companionlite.data.model.FamilyLinkDto
import com.companionlite.data.model.FeedbackType
import com.companionlite.data.model.MoodType
import com.companionlite.data.model.UserProfile
import java.time.LocalDate
import java.time.LocalTime

/**
 * 数据仓库接口 —— 界面对后端的全部依赖都收在这里。
 *
 * 为什么要有接口？
 * 现在有两种实现，页面用同一个接口就能切换：
 * - [RemoteCompanionRepository]：连 C 的后端，真实读写；
 * - [DemoCompanionRepository]：读 A 的 MockRepository，断网/答辩现场也能演示。
 *
 * 页面和 ViewModel 只依赖这个接口，不关心数据是哪个实现给的。
 * 返回值统一是 [UiState]，所以"加载中/失败/成功"是类型层面的，页面不会忘记处理失败。
 *
 * 时间参数 [days]：查最近几天，用 UTC 时刻算区间（api.md 规定时间一律 ISO-8601 UTC）。
 */
interface CompanionRepository {

    // ---------- 认证 ----------
    suspend fun login(username: String, password: String): UiState<UserProfile>
    suspend fun register(
        username: String,
        password: String,
        displayName: String,
        role: String,               // elder / family
        phone: String? = null
    ): UiState<UserProfile>
    suspend fun me(): UiState<UserProfile>
    fun logout()

    // ---------- 生活记录 ----------
    /** 今天的签到；返回 null 表示今天还没签到（**不等于**"今天没活动"） */
    suspend fun todayCheckIn(): UiState<DailyCheckIn?>
    suspend fun submitCheckIn(
        status: CheckInStatus,
        mood: MoodType?,
        note: String?,
        wantFamilyCall: Boolean = false
    ): UiState<DailyCheckIn>

    suspend fun checkIns(days: Int = 14): UiState<List<DailyCheckIn>>
    suspend fun activities(days: Int = 14): UiState<List<ActivityRecord>>
    suspend fun createActivity(
        type: ActivityType,
        note: String?,
        recordedAt: String? = null
    ): UiState<ActivityRecord>

    // ---------- 分析与关怀 ----------
    suspend fun baseline(): UiState<BaselineProfile>
    suspend fun careEvents(status: String? = null): UiState<List<CareEvent>>
    suspend fun submitFeedback(eventId: Long, feedback: FeedbackType): UiState<CareEvent>
    suspend fun updateEventStatus(eventId: Long, status: CareEventStatus): UiState<CareEvent>

    // ---------- 家庭 ----------
    /**
     * 家属端操作。
     * 说明：这里暂时直接返回 [FamilyLinkDto]，因为家属端页面还没并进来；
     * 等页面落地时再和 A 一起定一个展示用的 FamilyLink 模型，不着急现在加。
     */
    suspend fun familyMembers(): UiState<List<FamilyMember>>
    suspend fun createInviteCode(): UiState<String>
    suspend fun bindFamily(inviteCode: String, relation: String? = null): UiState<FamilyLinkDto>
    suspend fun confirmBind(linkId: Long): UiState<FamilyLinkDto>
    suspend fun updateFamilyLink(
        linkId: Long,
        status: String? = null,
        canViewStatus: Boolean? = null,
        canViewActivity: Boolean? = null,
        canViewFeedback: Boolean? = null,
        canReceiveAlerts: Boolean? = null
    ): UiState<FamilyLinkDto>
}

/**
 * 离线演示实现：直接读 A 的 [MockRepository]，不碰网络。
 *
 * 用途很具体：答辩现场没有网、或者 C 的后端还没跑起来的时候，
 * App 仍然能完整走一遍「签到 → 基线 → 主动询问 → 本人反馈」。
 *
 * ⚠️ 这里所有数据都是**模拟数据**，界面上必须继续显示「演示数据」标识，
 *    不能因为换了个实现就让人以为是真实采集。
 */
class DemoCompanionRepository : CompanionRepository {

    private var answered: FeedbackType? = null

    override suspend fun login(username: String, password: String): UiState<UserProfile> =
        UiState.Success(MockRepository.demoUser)

    override suspend fun register(
        username: String,
        password: String,
        displayName: String,
        role: String,
        phone: String?
    ): UiState<UserProfile> = UiState.Success(
        MockRepository.demoUser.copy(name = displayName.ifBlank { username })
    )

    override suspend fun me(): UiState<UserProfile> = UiState.Success(MockRepository.demoUser)

    override fun logout() = Unit

    override suspend fun todayCheckIn(): UiState<DailyCheckIn?> =
        UiState.Success(MockRepository.todayCheckIn)

    override suspend fun submitCheckIn(
        status: CheckInStatus,
        mood: MoodType?,
        note: String?,
        wantFamilyCall: Boolean
    ): UiState<DailyCheckIn> = UiState.Success(
        DailyCheckIn(
            date = LocalDate.now(),
            time = LocalTime.now(),
            status = status,
            mood = mood,
            note = note.orEmpty()
        )
    )

    override suspend fun checkIns(days: Int): UiState<List<DailyCheckIn>> =
        UiState.Success(MockRepository.checkIns.takeLast(days))

    override suspend fun activities(days: Int): UiState<List<ActivityRecord>> =
        UiState.Success(MockRepository.activities)

    override suspend fun createActivity(
        type: ActivityType,
        note: String?,
        recordedAt: String?
    ): UiState<ActivityRecord> = UiState.Success(
        ActivityRecord(
            id = System.currentTimeMillis(),
            type = type,
            date = LocalDate.now(),
            time = LocalTime.now(),
            note = note.orEmpty()
        )
    )

    override suspend fun baseline(): UiState<BaselineProfile> =
        UiState.Success(MockRepository.baseline)

    override suspend fun careEvents(status: String?): UiState<List<CareEvent>> =
        UiState.Success(if (answered == null) listOf(MockRepository.careEvent) else emptyList())

    override suspend fun submitFeedback(eventId: Long, feedback: FeedbackType): UiState<CareEvent> {
        answered = feedback
        return UiState.Success(
            MockRepository.careEvent.copy(
                status = when (feedback) {
                    FeedbackType.WANT_CALL -> CareEventStatus.AWAITING_FAMILY
                    FeedbackType.NO_ANSWER -> CareEventStatus.PENDING
                    else -> CareEventStatus.CLOSED
                }
            )
        )
    }

    override suspend fun updateEventStatus(eventId: Long, status: CareEventStatus): UiState<CareEvent> =
        UiState.Success(MockRepository.careEvent.copy(status = status))

    override suspend fun familyMembers(): UiState<List<FamilyMember>> =
        UiState.Success(MockRepository.demoFamily)

    override suspend fun createInviteCode(): UiState<String> =
        UiState.Success(MockRepository.demoUser.inviteCode)

    override suspend fun bindFamily(inviteCode: String, relation: String?): UiState<FamilyLinkDto> =
        UiState.Error("演示模式下不能真的绑定，请连上后端后再试")

    override suspend fun confirmBind(linkId: Long): UiState<FamilyLinkDto> =
        UiState.Error("演示模式下不能真的绑定，请连上后端后再试")

    override suspend fun updateFamilyLink(
        linkId: Long,
        status: String?,
        canViewStatus: Boolean?,
        canViewActivity: Boolean?,
        canViewFeedback: Boolean?,
        canReceiveAlerts: Boolean?
    ): UiState<FamilyLinkDto> = UiState.Error("演示模式下不能真的修改授权，请连上后端后再试")
}
