package com.companionlite.ui.screens.auth

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 登录 / 注册页共用的 ViewModel。
 *
 * 现在只做本地格式校验，真正的账号密码校验由成员 C 的后端接口完成。
 * 成员 B 接入后，把 login() 里的最后两行换成调用 Repository 的挂起函数即可，
 * 页面代码一行都不用改。
 */
data class AuthUiState(
    val phone: String = "",
    val password: String = "",
    val name: String = "",
    val isFamily: Boolean = false,
    val error: String? = null,
    val isSubmitting: Boolean = false,
    val isLoggedIn: Boolean = false,
    val isRegistered: Boolean = false
)

class AuthViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    fun onPhoneChange(value: String) {
        _uiState.value = _uiState.value.copy(phone = value, error = null)
    }

    fun onPasswordChange(value: String) {
        _uiState.value = _uiState.value.copy(password = value, error = null)
    }

    fun onNameChange(value: String) {
        _uiState.value = _uiState.value.copy(name = value, error = null)
    }

    fun onRoleChange(isFamily: Boolean) {
        _uiState.value = _uiState.value.copy(isFamily = isFamily, error = null)
    }

    fun login() {
        val current = _uiState.value
        if (current.phone.isBlank()) {
            _uiState.value = current.copy(error = "请填写手机号")
            return
        }
        if (current.phone.length != 11) {
            _uiState.value = current.copy(error = "手机号应该是 11 位数字")
            return
        }
        if (current.password.length < 6) {
            _uiState.value = current.copy(error = "密码至少 6 位")
            return
        }
        // TODO(成员 B)：这里改成调用后端登录接口，成功后保存 token
        _uiState.value = current.copy(isSubmitting = true, error = null)
        _uiState.value = _uiState.value.copy(isSubmitting = false, isLoggedIn = true)
    }

    fun register() {
        val current = _uiState.value
        if (current.name.isBlank()) {
            _uiState.value = current.copy(error = "请填写称呼")
            return
        }
        if (current.phone.length != 11) {
            _uiState.value = current.copy(error = "手机号应该是 11 位数字")
            return
        }
        if (current.password.length < 6) {
            _uiState.value = current.copy(error = "密码至少 6 位")
            return
        }
        // TODO(成员 B)：这里改成调用后端注册接口
        _uiState.value = current.copy(isSubmitting = true, error = null)
        _uiState.value = _uiState.value.copy(isSubmitting = false, isRegistered = true)
    }
}
