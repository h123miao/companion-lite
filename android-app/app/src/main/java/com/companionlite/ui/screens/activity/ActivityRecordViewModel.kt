package com.companionlite.ui.screens.activity

import androidx.lifecycle.ViewModel
import com.companionlite.data.mock.MockRepository
import com.companionlite.data.model.ActivityRecord
import com.companionlite.data.model.ActivityType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalTime

data class ActivityUiState(
    val type: ActivityType? = null,
    val note: String = "",
    val currentTimeText: String = "",
    val todayRecords: List<ActivityRecord> = emptyList(),
    val error: String? = null,
    val submitted: Boolean = false
)

/**
 * 记录活动的 ViewModel。
 * 时间先默认取「现在」，第二版再支持手动选择时间（需要 DatePicker，由 A 下次迭代做）。
 */
class ActivityRecordViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(
        ActivityUiState(
            currentTimeText = nowText(),
            todayRecords = MockRepository.activities.filter { it.date == java.time.LocalDate.now() }
        )
    )
    val uiState: StateFlow<ActivityUiState> = _uiState.asStateFlow()

    fun onTypeChange(type: ActivityType) {
        _uiState.value = _uiState.value.copy(type = type, error = null)
    }

    fun onNoteChange(note: String) {
        _uiState.value = _uiState.value.copy(note = note)
    }

    fun submit() {
        val current = _uiState.value
        val type = current.type
        if (type == null) {
            _uiState.value = current.copy(error = "请先选择活动类型")
            return
        }
        // TODO(成员 B)：调用后端 POST /api/v1/activities
        val newRecord = ActivityRecord(
            id = (current.todayRecords.maxOfOrNull { it.id } ?: 0L) + 1,
            type = type,
            date = java.time.LocalDate.now(),
            time = LocalTime.now(),
            note = current.note
        )
        _uiState.value = current.copy(
            todayRecords = listOf(newRecord) + current.todayRecords,
            type = null,
            note = "",
            error = null,
            submitted = true
        )
    }

    fun resetSubmitted() {
        _uiState.value = _uiState.value.copy(submitted = false)
    }

    private fun nowText(): String {
        val time = LocalTime.now()
        return String.format("%02d:%02d", time.hour, time.minute)
    }
}
