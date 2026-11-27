package com.companionlite.data.remote

import android.content.Context
import android.content.SharedPreferences
import com.companionlite.BuildConfig
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * 网络客户端与登录态（成员 B 负责）。
 *
 * 后端地址在哪配？
 * - 模拟器访问本机后端：`http://10.0.2.2:8000/`（10.0.2.2 是模拟器看到的"你的电脑"）
 * - 手机真机：改成电脑的局域网 IP，例如 `http://192.168.1.5:8000/`
 * - 改 `app/build.gradle.kts` 里的 `BASE_URL`（已经留好这个字段），改完重新运行即可。
 * - 注意地址**结尾必须带 `/`**，Retrofit 的规矩，少了会在运行时抛异常。
 *
 * 登录态怎么持久化？
 * 调用 [init] 一次即可（在 Application.onCreate 里最合适）。
 * 现在还没调——因为那要改 A 的 MainActivity / Manifest，按 README 的边界得先跟 A 说一声。
 * 没调用也不会崩，只是杀掉进程后需要重新登录。
 */
object ApiClient {

    private const val PREFS_NAME = "companion_session"
    private const val KEY_TOKEN = "access_token"
    private const val KEY_USER_ID = "user_id"
    private const val KEY_ROLE = "role"
    private const val KEY_NAME = "display_name"

    private var prefs: SharedPreferences? = null

    /** 可选初始化：传进来 Application 或 Activity 的 Context 就能记住登录态 */
    fun init(context: Context) {
        prefs = context.applicationContext
            .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .also { restore(it) }
    }

    // ---------------- 登录态 ----------------

    @Volatile
    var token: String? = null
        private set

    @Volatile
    var userId: Int = -1
        private set

    @Volatile
    var role: String = "elder"
        private set

    @Volatile
    var displayName: String = ""
        private set

    val isLoggedIn: Boolean get() = !token.isNullOrBlank()

    fun saveSession(accessToken: String, user: com.companionlite.data.model.UserDto) {
        token = accessToken
        userId = user.id
        role = user.role
        displayName = user.displayName
        prefs?.edit()
            ?.putString(KEY_TOKEN, accessToken)
            ?.putInt(KEY_USER_ID, user.id)
            ?.putString(KEY_ROLE, user.role)
            ?.putString(KEY_NAME, user.displayName)
            ?.apply()
    }

    fun clear() {
        token = null
        userId = -1
        role = "elder"
        displayName = ""
        prefs?.edit()?.clear()?.apply()
    }

    private fun restore(p: SharedPreferences) {
        token = p.getString(KEY_TOKEN, null)
        userId = p.getInt(KEY_USER_ID, -1)
        role = p.getString(KEY_ROLE, "elder") ?: "elder"
        displayName = p.getString(KEY_NAME, "") ?: ""
    }

    // ---------------- Retrofit ----------------

    private val httpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            // 老人家里网络往往不好，超时给短一点，让界面早点说"连不上"，而不是一直转圈
            .connectTimeout(8, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .apply {
                if (BuildConfig.DEBUG) {
                    // 只在 debug 打日志：release 包打印请求头会把 token 写进日志
                    addInterceptor(
                        HttpLoggingInterceptor().apply {
                            level = HttpLoggingInterceptor.Level.BASIC
                        }
                    )
                }
            }
            .addInterceptor { chain ->
                val current = token
                val request = if (current.isNullOrBlank()) {
                    chain.request()
                } else {
                    chain.request().newBuilder()
                        .addHeader("Authorization", "Bearer $current")
                        .build()
                }
                chain.proceed(request)
            }
            .build()
    }

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
