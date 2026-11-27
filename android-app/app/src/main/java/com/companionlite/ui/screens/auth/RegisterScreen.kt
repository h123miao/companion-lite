package com.companionlite.ui.screens.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.ui.components.AppTopBar
import com.companionlite.ui.components.PrimaryButton
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.components.SelectableChip
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.TrustAlert

/**
 * 注册页。
 * 第一版只收「本人 / 家属」两种角色，家庭绑定在「我的」页面里用邀请码完成。
 */
@Composable
fun RegisterScreen(
    onBack: () -> Unit,
    onRegistered: () -> Unit,
    viewModel: AuthViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(state.isRegistered) {
        if (state.isRegistered) {
            onRegistered()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CreamBackground)
    ) {
        AppTopBar(title = "创建账号", onBack = onBack)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = Dimens.ScreenPadding)
                .padding(bottom = Dimens.GapXl)
        ) {
            Text(
                text = "你是本人的账号，还是家属的账号？",
                style = MaterialTheme.typography.titleMedium,
                color = InkText
            )
            Spacer(modifier = Modifier.height(Dimens.GapM))
            Row(modifier = Modifier.fillMaxWidth()) {
                SelectableChip(
                    text = "我是本人",
                    selected = !state.isFamily,
                    onClick = { viewModel.onRoleChange(false) },
                    modifier = Modifier.weight(1f)
                )
                Spacer(modifier = Modifier.width(Dimens.GapM))
                SelectableChip(
                    text = "我是家属",
                    selected = state.isFamily,
                    onClick = { viewModel.onRoleChange(true) },
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(Dimens.GapS))
            Text(
                text = "本人的账号用来签到、记录活动；家属的账号用来查看本人授权分享的状态。",
                style = MaterialTheme.typography.bodySmall,
                color = InkSoft
            )

            Spacer(modifier = Modifier.height(Dimens.GapXl))

            SectionCard(title = "账号信息") {
                OutlinedTextField(
                    value = state.username,
                    onValueChange = viewModel::onUsernameChange,
                    label = { Text("用户名") },
                    placeholder = { Text("3–50 位，登录时用它") },
                    singleLine = true,
                    shape = RoundedCornerShape(14.dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text),
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(Dimens.GapM))
                OutlinedTextField(
                    value = state.name,
                    onValueChange = viewModel::onNameChange,
                    label = { Text("怎么称呼你") },
                    placeholder = { Text("例如：王秀兰") },
                    singleLine = true,
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(Dimens.GapM))
                OutlinedTextField(
                    value = state.password,
                    onValueChange = viewModel::onPasswordChange,
                    label = { Text("设置密码") },
                    placeholder = { Text("至少 6 位") },
                    singleLine = true,
                    shape = RoundedCornerShape(14.dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    visualTransformation = PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth()
                )

                if (state.error != null) {
                    Spacer(modifier = Modifier.height(Dimens.GapM))
                    Text(
                        text = state.error.orEmpty(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = TrustAlert
                    )
                }

                Spacer(modifier = Modifier.height(Dimens.GapXl))

                PrimaryButton(
                    text = if (state.isSubmitting) "注册中…" else "注册",
                    onClick = viewModel::register,
                    enabled = !state.isSubmitting
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            Text(
                text = "注册后可以生成家庭邀请码，请家人用邀请码申请绑定；绑定需要你本人同意。",
                style = MaterialTheme.typography.bodySmall,
                color = InkSoft
            )
        }
    }
}
