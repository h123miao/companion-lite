package com.companionlite.ui.screens.checkin

import androidx.lifecycle.ViewModel
import com.companionlite.data.model.CheckInStatus
import com.companionlite.data.model.MoodType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class CheckInUiState(
    val status: CheckInStatus? = null,
    val mood: MoodType? = null,
    val note: String = "",
    val wantFamilyCall: Boolean = false,
    val error: String? = null,
    val submitted: Boolean = false
)

/**
 * 每日签到的 ViewModel。
 * 真实提交由成员 C 的 POST /api/v1/check-ins 接口完成（见 docs/api.md），
 * 现在点提交只改变界面状态，用来验证交互流程。
 */
class CheckInViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(CheckInUiState())
    val uiState: StateFlow<CheckInUiState> = _uiState.asStateFlow()

    fun onStatusChange(status: CheckInStatus) {
        _uiState.value = _uiState.value.copy(status = status, error = null)
    }

    fun onMoodChange(mood: MoodType) {
        _uiState.value = _uiState.value.copy(mood = mood)
    }

    fun onNoteChange(note: String) {
        _uiState.value = _uiState.value.copy(note = note)
    }

    fun onWantFamilyCallChange(checked: Boolean) {
        _uiState.value = _uiState.value.copy(wantFamilyCall = checked)
    }

    fun submit() {
        val current = _uiState.value
        if (current.status == null) {
            _uiState.value = current.copy(error = "请先选择今天身体的感觉")
            return
        }
        // TODO(成员 B)：调用后端提交签到，成功后再置 submitted = true
        _uiState.value = current.copy(submitted = true, error = null)
    }
}
