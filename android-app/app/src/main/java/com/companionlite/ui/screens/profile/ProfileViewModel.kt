package com.companionlite.ui.screens.profile

import androidx.lifecycle.ViewModel
import com.companionlite.data.mock.MockRepository
import com.companionlite.data.model.FamilyMember
import com.companionlite.data.model.UserProfile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class ProfileUiState(
    val user: UserProfile,
    val family: List<FamilyMember>,
    val shareStatusToFamily: Boolean = true,
    val allowFamilyAlert: Boolean = true,
    val showLogoutConfirm: Boolean = false
)

/**
 * 「我的」页面 ViewModel。
 *
 * 授权相关的开关只是界面层，**真正的权限校验必须在后端做**
 * （成员 C 负责）。前端隐藏按钮不算权限控制。
 */
class ProfileViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(
        ProfileUiState(
            user = MockRepository.demoUser,
            family = MockRepository.demoFamily
        )
    )
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun onShareStatusChange(checked: Boolean) {
        _uiState.value = _uiState.value.copy(shareStatusToFamily = checked)
    }

    fun onAllowAlertChange(checked: Boolean) {
        _uiState.value = _uiState.value.copy(allowFamilyAlert = checked)
    }

    fun onRequestLogout() {
        _uiState.value = _uiState.value.copy(showLogoutConfirm = true)
    }

    fun onDismissLogout() {
        _uiState.value = _uiState.value.copy(showLogoutConfirm = false)
    }
}
