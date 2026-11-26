package com.companionlite.ui.screens.stats

import androidx.lifecycle.ViewModel
import com.companionlite.data.mock.MockRepository
import com.companionlite.data.model.BaselineProfile
import com.companionlite.data.model.DailyCheckIn
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class StatsUiState(
    val baseline: BaselineProfile,
    val checkIns: List<DailyCheckIn>,
    val checkInBarValues: List<Float?>,
    val checkInBarLabels: List<String>,
    val activityCounts: List<Int>,
    val activityLabels: List<String>,
    val checkInRate: Float,
    val careEventTotal: Int,
    val careEventHandled: Int
)

/**
 * 生活规律统计页。
 * 注意：页面里的所有算法数字都来自 MockRepository.baseline（即成员 D 的算法结果），
 * 页面**不做任何计算**，只做归一化后画图。这样算法改了口径，界面自动跟着变。
 */
class StatsViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(buildState())
    val uiState: StateFlow<StatsUiState> = _uiState.asStateFlow()

    private fun buildState(): StatsUiState {
        val checkIns = MockRepository.checkIns
        val startMinute = 6 * 60
        val spanMinute = 6 * 60f

        val bars: List<Float?> = checkIns.map { checkIn ->
            checkIn.time?.let { time ->
                val minute = time.hour * 60 + time.minute
                ((minute - startMinute).toFloat() / spanMinute).coerceIn(0.05f, 1f)
            }
        }

        val labels = checkIns.map { "${it.date.monthValue}/${it.date.dayOfMonth}" }
        val valid = checkIns.count { it.time != null }

        return StatsUiState(
            baseline = MockRepository.baseline,
            checkIns = checkIns,
            checkInBarValues = bars,
            checkInBarLabels = labels,
            activityCounts = MockRepository.weeklyActivityCounts,
            activityLabels = MockRepository.recentDayLabels,
            checkInRate = valid.toFloat() / checkIns.size.toFloat(),
            careEventTotal = 2,
            careEventHandled = 1
        )
    }
}
