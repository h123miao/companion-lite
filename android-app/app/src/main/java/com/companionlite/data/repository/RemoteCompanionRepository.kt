package com.companionlite.data.repository

import com.companionlite.data.UiState
import com.companionlite.data.model.ActivityRecord
import com.companionlite.data.model.ActivityRequest
import com.companionlite.data.model.ActivityType
import com.companionlite.data.model.BaselineProfile
import com.companionlite.data.model.BindRequest
import com.companionlite.data.model.CareEvent
import com.companionlite.data.model.CareEventStatus
import com.companionlite.data.model.CheckInRequest
import com.companionlite.data.model.CheckInStatus
import com.companionlite.data.model.DailyCheckIn
import com.companionlite.data.model.EventStatusRequest
import com.companionlite.data.model.FamilyLinkDto
import com.companionlite.data.model.FamilyLinkUpdateRequest
import com.companionlite.data.model.FamilyMember
import com.companionlite.data.model.FeedbackRequest
import com.companionlite.data.model.FeedbackType
import com.companionlite.data.model.LoginRequest
import com.companionlite.data.model.Mappers
import com.companionlite.data.model.MoodType
import com.companionlite.data.model.RegisterRequest
import com.companionlite.data.model.UserProfile
import com.companionlite.data.remote.ApiClient
import com.companionlite.data.remote.ApiService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.HttpException
import java.io.IOException
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.temporal.ChronoUnit

/**
 * 真实实现：所有数据都来自 C 的 FastAPI 后端。
 *
 * 三个设计点，都是踩过坑才这么写的：
 *
 * 1. **网络异常必须翻译成人话。** 用户不会理解 `java.net.ConnectException`，
 *    所以 IOException 统一说成"连不上服务器，请确认后端已启动"，
 *    403 统一说成"没有权限"（典型场景：家属没被授权却想查本人数据）。
 *
 * 2. **读和写分开处理。** 读失败可以退回演示数据（界面有东西可看）；
 *    写失败（签到、回答）绝不能假装成功——那是在骗用户，比报错严重得多。
 *
 * 3. **DTO 到界面模型的转换放在 [Mappers] 里，且不抛异常。**
 *    某一条数据格式不对，只有那一条显示不出来，页面不会崩。
 */
class RemoteCompanionRepository(
    private val api: ApiService = ApiClient.api
) : CompanionRepository {

    // ---------------- 统一错误处理 ----------------

    private fun friendlyMessage(e: Exception): String = when (e) {
        is IOException -> "连不上服务器。请确认后端已启动，或检查手机和电脑是否在同一个 WiFi。"
        is HttpException -> when (e.code()) {
            401 -> "登录已过期，请重新登录"
            403 -> "没有权限查看这些数据（家属需要本人授权后才能查看）"
            404 -> "找不到对应的数据"
            409 -> "当前状态不允许这么做（比如今天已经签过到了）"
            in 500..599 -> "服务器出错了（${e.code()}），请稍后再试"
            else -> "请求没有被接受（${e.code()}）"
        }
        else -> e.message?.take(120) ?: "未知错误"
    }

    private suspend fun <T> read(block: suspend () -> T): UiState<T> =
        withContext(Dispatchers.IO) {
            try {
                UiState.Success(block())
            } catch (e: Exception) {
                UiState.Error(friendlyMessage(e))
            }
        }

    private suspend fun <T> write(block: suspend () -> T): UiState<T> = read(block)

    // ---------------- 时间区间 ----------------

    /** 最近 [days] 天的起点，ISO-8601 UTC */
    private fun fromInstant(days: Int): String =
        Instant.now().minus(days.toLong(), ChronoUnit.DAYS).toString()

    private fun nowInstant(): String = Instant.now().toString()

    // ---------------- 认证 ----------------

    override suspend fun login(username: String, password: String): UiState<UserProfile> =
        read {
            val response = api.login(LoginRequest(username.trim(), password))
            // 拿到 token 立刻存下来，后面每个请求的拦截器都要用它
            ApiClient.saveSession(response.accessToken, response.user)
            Mappers.toUserProfile(response.user)
        }

    override suspend fun register(
        username: String,
        password: String,
        displayName: String,
        role: String,
        phone: String?
    ): UiState<UserProfile> = read {
        val response = api.register(
            RegisterRequest(
                username = username.trim(),
                password = password,
                displayName = displayName.ifBlank { username.trim() },
                role = role,
                phone = phone?.ifBlank { null }
            )
        )
        ApiClient.saveSession(response.accessToken, response.user)
        Mappers.toUserProfile(response.user)
    }

    override suspend fun me(): UiState<UserProfile> = read {
        Mappers.toUserProfile(api.me())
    }

    override fun logout() = ApiClient.clear()

    // ---------------- 生活记录 ----------------

    /**
     * 今天的签到。
     * api.md 没有 `/check-ins/today`，所以按区间查再本地挑出今天那条——
     * 不自己发明接口，是团队约定。
     */
    override suspend fun todayCheckIn(): UiState<DailyCheckIn?> = read {
        val today = LocalDate.now()
        val zone = ZoneId.systemDefault()
        val from = today.atStartOfDay(zone).toInstant().toString()
        val to = today.plusDays(1).atStartOfDay(zone).toInstant().toString()
        api.checkIns(from, to)
            .mapNotNull(Mappers::toDailyCheckIn)
            .firstOrNull { it.date == today }
    }

    override suspend fun submitCheckIn(
        status: CheckInStatus,
        mood: MoodType?,
        note: String?,
        wantFamilyCall: Boolean
    ): UiState<DailyCheckIn> = read {
        val dto = api.createCheckIn(
            CheckInRequest(
                status = Mappers.checkInStatusToWire(status),
                mood = Mappers.moodToWire(mood),
                note = note?.ifBlank { null },
                wantFamilyCall = wantFamilyCall
            )
        )
        // 后端返回的时间解析不出来时，用本地时间兜底，至少让界面能显示"已签到"
        Mappers.toDailyCheckIn(dto) ?: DailyCheckIn(
            date = LocalDate.now(),
            time = java.time.LocalTime.now(),
            status = status,
            mood = mood,
            note = note.orEmpty()
        )
    }

    override suspend fun checkIns(days: Int): UiState<List<DailyCheckIn>> = read {
        api.checkIns(fromInstant(days), nowInstant())
            .mapNotNull(Mappers::toDailyCheckIn)
    }

    override suspend fun activities(days: Int): UiState<List<ActivityRecord>> = read {
        api.activities(fromInstant(days), nowInstant())
            .mapNotNull(Mappers::toActivityRecord)
    }

    override suspend fun createActivity(
        type: ActivityType,
        note: String?,
        recordedAt: String?
    ): UiState<ActivityRecord> = read {
        val dto = api.createActivity(
            ActivityRequest(
                activityType = Mappers.activityTypeToWire(type),
                recordedAt = recordedAt ?: nowInstant(),
                note = note?.ifBlank { null }
            )
        )
        Mappers.toActivityRecord(dto) ?: throw IllegalStateException("后端返回的活动记录时间格式无法解析")
    }

    // ---------------- 分析与关怀 ----------------

    override suspend fun baseline(): UiState<BaselineProfile> = read {
        Mappers.toBaseline(api.baseline())
    }

    override suspend fun careEvents(status: String?): UiState<List<CareEvent>> = read {
        api.careEvents(status).map(Mappers::toCareEvent)
    }

    override suspend fun submitFeedback(eventId: Long, feedback: FeedbackType): UiState<CareEvent> =
        read {
            val dto = api.submitFeedback(
                eventId.toInt(),
                FeedbackRequest(Mappers.feedbackTypeToWire(feedback))
            )
            Mappers.toCareEvent(dto)
        }

    override suspend fun updateEventStatus(
        eventId: Long,
        status: CareEventStatus
    ): UiState<CareEvent> = read {
        val wire = when (status) {
            CareEventStatus.PENDING -> "pending"
            CareEventStatus.AWAITING_FAMILY -> "awaiting_family"
            CareEventStatus.HANDLED -> "handled"
            CareEventStatus.CLOSED -> "closed"
        }
        Mappers.toCareEvent(api.updateEventStatus(eventId.toInt(), EventStatusRequest(wire)))
    }

    // ---------------- 家庭 ----------------

    override suspend fun familyMembers(): UiState<List<FamilyMember>> = read {
        api.familyMembers().map(Mappers::toFamilyMember)
    }

    override suspend fun createInviteCode(): UiState<String> = read {
        api.createInviteCode().inviteCode
    }

    override suspend fun bindFamily(inviteCode: String, relation: String?): UiState<FamilyLinkDto> =
        write { api.bind(BindRequest(inviteCode.trim().uppercase(), relation)) }

    override suspend fun confirmBind(linkId: Long): UiState<FamilyLinkDto> =
        write { api.confirmBind(linkId.toInt()) }

    override suspend fun updateFamilyLink(
        linkId: Long,
        status: String?,
        canViewStatus: Boolean?,
        canViewActivity: Boolean?,
        canViewFeedback: Boolean?,
        canReceiveAlerts: Boolean?
    ): UiState<FamilyLinkDto> = write {
        api.updateFamilyLink(
            linkId.toInt(),
            FamilyLinkUpdateRequest(
                status = status,
                canViewStatus = canViewStatus,
                canViewActivity = canViewActivity,
                canViewFeedback = canViewFeedback,
                canReceiveAlerts = canReceiveAlerts
            )
        )
    }
}
