package com.companionlite.ui.screens.home

import androidx.lifecycle.ViewModel
import com.companionlite.data.mock.MockRepository
import com.companionlite.data.model.ActivityRecord
import com.companionlite.data.model.BaselineProfile
import com.companionlite.data.model.CareEvent
import com.companionlite.data.model.DailyCheckIn
import com.companionlite.data.model.FeedbackType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDate
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.util.Locale

/** 首页需要的全部界面状态，页面本身不持有任何数据 */
data class HomeUiState(
    val greeting: String = "",
    val dateText: String = "",
    val userName: String = "",
    val todayCheckIn: DailyCheckIn? = null,
    val baseline: BaselineProfile,
    val recentActivities: List<ActivityRecord> = emptyList(),
    val careEvent: CareEvent? = null,
    val answeredFeedback: FeedbackType? = null,
    val careDialogVisible: Boolean = false,
    val recentCheckIns: List<DailyCheckIn> = emptyList()
)

class HomeViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(buildInitialState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    /** 打开主动询问弹窗 */
    fun openCareDialog() {
        val current = _uiState.value
        if (current.careEvent != null && current.answeredFeedback == null) {
            _uiState.value = current.copy(careDialogVisible = true)
        }
    }

    fun dismissCareDialog() {
        _uiState.value = _uiState.value.copy(careDialogVisible = false)
    }

    /**
     * 本人回答了主动询问。
     * 真实项目中这一步会调用后端接口，更新关怀事件状态；
     * 现在只更新界面，用来演示「询问 → 反馈 → 事件状态变化」这条闭环。
     */
    fun answerCareEvent(feedback: FeedbackType) {
        _uiState.value = _uiState.value.copy(
            careDialogVisible = false,
            answeredFeedback = feedback,
            careEvent = null
        )
    }

    private fun buildInitialState(): HomeUiState {
        val now = LocalTime.now()
        return HomeUiState(
            greeting = greetingOf(now.hour),
            dateText = LocalDate.now().format(
                DateTimeFormatter.ofPattern("M月d日 EEEE", Locale.CHINA)
            ),
            userName = MockRepository.demoUser.name,
            todayCheckIn = MockRepository.todayCheckIn,
            baseline = MockRepository.baseline,
            recentActivities = MockRepository.activities.take(3),
            careEvent = MockRepository.careEvent,
            recentCheckIns = MockRepository.checkIns.takeLast(7)
        )
    }

    private fun greetingOf(hour: Int): String = when (hour) {
        in 0..5 -> "夜深了"
        in 6..8 -> "早上好"
        in 9..11 -> "上午好"
        in 12..13 -> "中午好"
        in 14..17 -> "下午好"
        else -> "晚上好"
    }
}
