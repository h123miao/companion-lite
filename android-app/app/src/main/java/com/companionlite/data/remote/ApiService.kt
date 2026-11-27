package com.companionlite.data.remote

import com.companionlite.data.model.ActivityDto
import com.companionlite.data.model.ActivityRequest
import com.companionlite.data.model.BaselineDto
import com.companionlite.data.model.BindRequest
import com.companionlite.data.model.CareEventDto
import com.companionlite.data.model.CheckInDto
import com.companionlite.data.model.CheckInRequest
import com.companionlite.data.model.EventStatusRequest
import com.companionlite.data.model.FamilyLinkDto
import com.companionlite.data.model.FamilyLinkUpdateRequest
import com.companionlite.data.model.FeedbackRequest
import com.companionlite.data.model.InviteCodeDto
import com.companionlite.data.model.LoginRequest
import com.companionlite.data.model.LoginResponse
import com.companionlite.data.model.RegisterRequest
import com.companionlite.data.model.UserDto
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * 后端接口声明（成员 B 负责）。
 *
 * 路径严格照 `docs/api.md` 第 3 节的清单写：前缀 `/api/v1`，具体路径一个字母都没有自己改。
 * api.md 里没有的接口，这里也不出现——需要新接口时先在群里问 C，由 C 写进 api.md 再加。
 *
 * 认证：所有需要登录的接口都由 [ApiClient] 的拦截器统一加
 * `Authorization: Bearer <token>`，这里不用每个方法都写 @Header。
 */
interface ApiService {

    // ---------------- 用户与家庭（api.md 3.1） ----------------

    @POST("api/v1/auth/register")
    suspend fun register(@Body body: RegisterRequest): LoginResponse

    @POST("api/v1/auth/login")
    suspend fun login(@Body body: LoginRequest): LoginResponse

    @GET("api/v1/users/me")
    suspend fun me(): UserDto

    @POST("api/v1/family/invite-code")
    suspend fun createInviteCode(): InviteCodeDto

    @POST("api/v1/family/bind")
    suspend fun bind(@Body body: BindRequest): FamilyLinkDto

    @POST("api/v1/family/bind/{linkId}/confirm")
    suspend fun confirmBind(@Path("linkId") linkId: Int): FamilyLinkDto

    @GET("api/v1/family/members")
    suspend fun familyMembers(): List<FamilyLinkDto>

    @PATCH("api/v1/family/links/{linkId}")
    suspend fun updateFamilyLink(
        @Path("linkId") linkId: Int,
        @Body body: FamilyLinkUpdateRequest
    ): FamilyLinkDto

    // ---------------- 生活记录（api.md 3.2） ----------------

    @POST("api/v1/check-ins")
    suspend fun createCheckIn(@Body body: CheckInRequest): CheckInDto

    @GET("api/v1/check-ins")
    suspend fun checkIns(
        @Query("from") from: String,
        @Query("to") to: String
    ): List<CheckInDto>

    @POST("api/v1/activities")
    suspend fun createActivity(@Body body: ActivityRequest): ActivityDto

    @GET("api/v1/activities")
    suspend fun activities(
        @Query("from") from: String,
        @Query("to") to: String
    ): List<ActivityDto>

    // ---------------- 分析与关怀（api.md 3.3） ----------------

    @GET("api/v1/baseline")
    suspend fun baseline(): BaselineDto

    @GET("api/v1/care-events")
    suspend fun careEvents(@Query("status") status: String? = null): List<CareEventDto>

    @POST("api/v1/care-events/{id}/feedback")
    suspend fun submitFeedback(
        @Path("id") eventId: Int,
        @Body body: FeedbackRequest
    ): CareEventDto

    @PATCH("api/v1/care-events/{id}/status")
    suspend fun updateEventStatus(
        @Path("id") eventId: Int,
        @Body body: EventStatusRequest
    ): CareEventDto
}
