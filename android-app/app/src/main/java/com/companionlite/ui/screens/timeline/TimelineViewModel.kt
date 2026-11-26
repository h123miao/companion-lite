package com.companionlite.ui.screens.timeline

import androidx.lifecycle.ViewModel
import com.companionlite.data.mock.MockRepository
import com.companionlite.data.model.DataTrustState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.DayOfWeek
import java.time.LocalDate

/** 时间线的筛选条件 */
enum class TimelineFilter(val label: String) {
    ALL("全部"),
    CHECK_IN("签到"),
    ACTIVITY("活动")
}

/** 时间线里的一条记录（签到和活动被统一成同一种展示结构，页面就不用关心数据来源） */
data class TimelineEntry(
    val date: LocalDate,
    val timeText: String,
    val title: String,
    val subtitle: String,
    val trust: DataTrustState,
    val kind: TimelineFilter
)

data class TimelineDayGroup(
    val dayLabel: String,
    val dateLabel: String,
    val entries: List<TimelineEntry>
)

data class TimelineUiState(
    val filter: TimelineFilter = TimelineFilter.ALL,
    val groups: List<TimelineDayGroup> = emptyList(),
    val checkInDays: Int = 0,
    val activityCount: Int = 0
)

/**
 * 历史记录时间线的 ViewModel。
 *
 * 重要设计：签到和活动是两种数据，但在时间线里都显示成「时间 + 标题 + 状态」，
 * 缺失的那一天显示成「没有收到签到记录」+ 灰色标签，而不是空着。
 */
class TimelineViewModel : ViewModel() {

    private val allCheckIns = MockRepository.checkIns
    private val allActivities = MockRepository.activities

    private val _uiState = MutableStateFlow(buildState(TimelineFilter.ALL))
    val uiState: StateFlow<TimelineUiState> = _uiState.asStateFlow()

    fun onFilterChange(filter: TimelineFilter) {
        _uiState.value = buildState(filter)
    }

    private fun buildState(filter: TimelineFilter): TimelineUiState {
        val checkInEntries = allCheckIns.map { checkIn ->
            TimelineEntry(
                date = checkIn.date,
                timeText = checkIn.time?.let { String.format("%02d:%02d", it.hour, it.minute) } ?: "--:--",
                title = if (checkIn.time == null) "没有收到签到记录" else "每日签到",
                subtitle = if (checkIn.time == null) {
                    "设备在线，但今天没有你的签到记录"
                } else {
                    val body = checkIn.status?.label ?: "未填写"
                    val mood = checkIn.mood?.label
                    if (mood != null) "$body · 心情 $mood" else body
                },
                trust = checkIn.trust,
                kind = TimelineFilter.CHECK_IN
            )
        }

        val activityEntries = allActivities.map { activity ->
            TimelineEntry(
                date = activity.date,
                timeText = String.format("%02d:%02d", activity.time.hour, activity.time.minute),
                title = activity.type.label,
                subtitle = if (activity.note.isBlank()) activity.source else activity.note,
                trust = activity.trust,
                kind = TimelineFilter.ACTIVITY
            )
        }

        val filtered = when (filter) {
            TimelineFilter.ALL -> checkInEntries + activityEntries
            TimelineFilter.CHECK_IN -> checkInEntries
            TimelineFilter.ACTIVITY -> activityEntries
        }

        val groups = filtered
            .groupBy { it.date }
            .toSortedMap(compareByDescending { it })
            .map { (date, entries) ->
                TimelineDayGroup(
                    dayLabel = dayLabelOf(date),
                    dateLabel = "${date.monthValue}月${date.dayOfMonth}日 ${weekdayOf(date)}",
                    entries = entries.sortedByDescending { it.timeText }
                )
            }

        return TimelineUiState(
            filter = filter,
            groups = groups,
            checkInDays = allCheckIns.count { it.time != null },
            activityCount = allActivities.size
        )
    }

    private fun dayLabelOf(date: LocalDate): String {
        val today = LocalDate.now()
        return when (date) {
            today -> "今天"
            today.minusDays(1) -> "昨天"
            today.minusDays(2) -> "前天"
            else -> "${date.monthValue}月${date.dayOfMonth}日"
        }
    }

    private fun weekdayOf(date: LocalDate): String = when (date.dayOfWeek) {
        DayOfWeek.MONDAY -> "周一"
        DayOfWeek.TUESDAY -> "周二"
        DayOfWeek.WEDNESDAY -> "周三"
        DayOfWeek.THURSDAY -> "周四"
        DayOfWeek.FRIDAY -> "周五"
        DayOfWeek.SATURDAY -> "周六"
        DayOfWeek.SUNDAY -> "周日"
    }
}
