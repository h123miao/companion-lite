package com.companionlite.ui.screens.auth

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 登录 / 注册页共用的 ViewModel。
 *
 * 账号体例已和后端对齐（docs/api.md v2.0）：
 *   POST /api/v1/auth/register  { username, password, display_name, role }
 *   POST /api/v1/auth/login     { username, password }
 * 所以登录用的是**用户名**（3–50 位），不是手机号；手机号只是可选资料。
 *
 * 现在只做本地格式校验，真正的账号密码校验由成员 C 的后端完成。
 * 成员 B 接好后，把 login() 最后两行换成调用 Repository 的挂起函数即可，
 * 页面代码一行都不用改。
 */
data class AuthUiState(
    val username: String = "",
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

    fun onUsernameChange(value: String) {
        _uiState.value = _uiState.value.copy(username = value, error = null)
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
        when {
            current.username.isBlank() -> {
                _uiState.value = current.copy(error = "请填写用户名")
                return
            }
            current.username.length !in 3..50 -> {
                _uiState.value = current.copy(error = "用户名要 3–50 位")
                return
            }
            current.password.length < 6 -> {
                _uiState.value = current.copy(error = "密码至少 6 位")
                return
            }
        }
        // TODO(成员 B)：这里改成调用后端登录接口，成功后保存 token
        _uiState.value = current.copy(isSubmitting = true, error = null)
        _uiState.value = _uiState.value.copy(isSubmitting = false, isLoggedIn = true)
    }

    fun register() {
        val current = _uiState.value
        when {
            current.name.isBlank() -> {
                _uiState.value = current.copy(error = "请填写称呼")
                return
            }
            current.username.length !in 3..50 -> {
                _uiState.value = current.copy(error = "用户名要 3–50 位")
                return
            }
            current.password.length < 6 -> {
                _uiState.value = current.copy(error = "密码至少 6 位")
                return
            }
        }
        // TODO(成员 B)：这里改成调用后端注册接口
        _uiState.value = current.copy(isSubmitting = true, error = null)
        _uiState.value = _uiState.value.copy(isSubmitting = false, isRegistered = true)
    }
}
