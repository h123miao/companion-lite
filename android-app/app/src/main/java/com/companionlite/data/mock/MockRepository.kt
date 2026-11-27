package com.companionlite.data.mock

import com.companionlite.data.model.ActivityRecord
import com.companionlite.data.model.ActivityType
import com.companionlite.data.model.BaselineProfile
import com.companionlite.data.model.CareEvent
import com.companionlite.data.model.CareEventStatus
import com.companionlite.data.model.CheckInStatus
import com.companionlite.data.model.DailyCheckIn
import com.companionlite.data.model.DataTrustState
import com.companionlite.data.model.FamilyMember
import com.companionlite.data.model.MoodType
import com.companionlite.data.model.UserProfile
import java.time.LocalDate
import java.time.LocalTime

/**
 * 模拟数据仓库（成员 A 的 UI 先用它跑通页面）。
 *
 * ⚠️ 这些全部是**模拟数据**，界面上必须显示「演示数据」标识。
 *    成员 B 接入后端后，把调用 MockRepository 的地方换成 Repository 的接口即可，
 *    页面代码不用改（因为页面只依赖 ViewModel 暴露的 UiState）。
 */
object MockRepository {

    const val DEMO_TAG = "演示数据"

    val demoUser = UserProfile(
        userId = 1001,
        name = "王秀兰",
        roleLabel = "本人",
        phone = "138****0001",
        inviteCode = "BX-7215"
    )

    val demoFamily = listOf(
        FamilyMember(name = "李梅", relation = "女儿", canViewStatus = true, canReceiveAlert = true),
        FamilyMember(name = "李强", relation = "儿子", canViewStatus = true, canReceiveAlert = false)
    )

    /**
     * 过去 14 天的签到记录。
     * 0 = 今天（故意留空：用于演示"今天还没有签到"的主动关怀流程）
     */
    private fun checkInPlan(): List<Pair<Int, LocalTime?>> = listOf(
        13 to LocalTime.of(7, 42),
        12 to LocalTime.of(7, 55),
        11 to LocalTime.of(8, 6),
        10 to LocalTime.of(7, 38),
        9 to null,
        8 to LocalTime.of(7, 50),
        7 to LocalTime.of(8, 12),
        6 to LocalTime.of(7, 44),
        5 to LocalTime.of(7, 58),
        4 to null,
        3 to LocalTime.of(7, 36),
        2 to LocalTime.of(10, 15),
        1 to LocalTime.of(7, 52),
        0 to null
    )

    val checkIns: List<DailyCheckIn>
        get() {
            val today = LocalDate.now()
            return checkInPlan().map { (offset, time) ->
                val date = today.minusDays(offset.toLong())
                if (time == null) {
                    DailyCheckIn(
                        date = date,
                        time = null,
                        status = null,
                        mood = null,
                        trust = if (offset == 0) DataTrustState.MISSING else DataTrustState.MISSING
                    )
                } else {
                    DailyCheckIn(
                        date = date,
                        time = time,
                        status = if (offset == 2) CheckInStatus.UNWELL else CheckInStatus.GOOD,
                        mood = if (offset == 2) MoodType.TIRED else MoodType.CALM,
                        note = if (offset == 2) "昨晚没睡好，起晚了" else "",
                        trust = DataTrustState.USER_FEEDBACK
                    )
                }
            }
        }

    /** 今天的签到记录（null 表示还没签到） */
    val todayCheckIn: DailyCheckIn?
        get() = checkIns.firstOrNull { it.date == LocalDate.now() && it.time != null }

    /** 最近 3 天的活动记录 */
    val activities: List<ActivityRecord>
        get() {
            val today = LocalDate.now()
            val list = mutableListOf<ActivityRecord>()
            var id = 1L
            fun add(offset: Long, type: ActivityType, h: Int, m: Int, note: String = "") {
                list += ActivityRecord(
                    id = id++,
                    type = type,
                    date = today.minusDays(offset),
                    time = LocalTime.of(h, m),
                    note = note
                )
            }
            // 今天
            add(0, ActivityType.WAKE, 6, 50, "今天起得早")
            add(0, ActivityType.MEAL, 7, 20, "小米粥")
            add(0, ActivityType.OUT, 9, 10, "去菜市场")
            add(0, ActivityType.HOME, 10, 40)
            add(0, ActivityType.MEAL, 12, 5)
            add(0, ActivityType.REST, 13, 30, "午睡")
            // 昨天
            add(1, ActivityType.WAKE, 7, 30)
            add(1, ActivityType.EXERCISE, 16, 0, "小区里走了 30 分钟")
            add(1, ActivityType.MEAL, 18, 20)
            // 前天
            add(2, ActivityType.WAKE, 9, 50, "昨晚没睡好")
            add(2, ActivityType.MEAL, 12, 30)
            add(2, ActivityType.MEDICINE, 20, 0, "降压药")
            return list
        }

    /**
     * 个人生活基线：真实项目中这些数字由成员 D 的算法算出来，
     * 通过 C 的接口返回；UI 只展示，不在这里重新实现算法。
     */
    val baseline = BaselineProfile(
        validDays = 11,
        medianCheckIn = LocalTime.of(7, 52),
        earliest = LocalTime.of(7, 36),
        latest = LocalTime.of(10, 15),
        spreadMinutes = 40,
        dailyActivityAvg = 4.6,
        trust = DataTrustState.NORMAL
    )

    /** 今天触发的关怀事件（用于演示主动询问） */
    val careEvent = CareEvent(
        id = 9001,
        triggerRule = "规则一：签到时间偏离个人规律",
        reason = "今天 10:30 还没有收到签到记录。你过去 14 天通常在 7:30—8:30 之间签到。",
        createdAtText = "今天 10:30",
        status = CareEventStatus.PENDING,
        trust = DataTrustState.MISSING
    )

    /** 本周（近 7 天）活动数量，用于统计页的小柱状图 */
    val weeklyActivityCounts: List<Int>
        get() = listOf(5, 4, 6, 3, 5, 4, 6)

    /** 近 7 天日期文本，用于图表横轴 */
    val recentDayLabels: List<String>
        get() {
            val today = LocalDate.now()
            return (6 downTo 0).map { offset ->
                val d = today.minusDays(offset.toLong())
                "${d.monthValue}/${d.dayOfMonth}"
            }
        }

    /** 演示账号（与后端注册体例一致：用户名 + 密码） */
    const val DEMO_USERNAME = "laowang"
    const val DEMO_PASSWORD = "123456"
}
