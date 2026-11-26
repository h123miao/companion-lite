package com.companionlite.ui.screens.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.ui.components.DemoBanner
import com.companionlite.ui.components.PrimaryButton
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.TrustAlert
import com.companionlite.ui.theme.WarmPrimary

/**
 * 登录页（本人和家属共用同一个入口，登录后由后端返回角色）。
 * 设计要点：一屏只做一件事，输入框大、按钮大、说明文字短。
 */
@Composable
fun LoginScreen(
    onLoggedIn: () -> Unit,
    onGoRegister: () -> Unit,
    viewModel: AuthViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(state.isLoggedIn) {
        if (state.isLoggedIn) {
            onLoggedIn()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CreamBackground)
            .statusBarsPadding()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = Dimens.ScreenPadding, vertical = Dimens.GapXl)
    ) {
        Spacer(modifier = Modifier.height(Dimens.GapXl))

        AppLogo()

        Spacer(modifier = Modifier.height(Dimens.GapL))

        Text(
            text = "伴行·时序",
            style = MaterialTheme.typography.displaySmall,
            color = InkText
        )
        Spacer(modifier = Modifier.height(Dimens.GapS))
        Text(
            text = "陪你把平常的日子，过得让人放心",
            style = MaterialTheme.typography.bodyLarge,
            color = InkSoft
        )

        Spacer(modifier = Modifier.height(Dimens.GapXxl))

        SectionCard {
            Text(
                text = "手机号登录",
                style = MaterialTheme.typography.titleMedium,
                color = InkText
            )
            Spacer(modifier = Modifier.height(Dimens.GapL))

            OutlinedTextField(
                value = state.phone,
                onValueChange = viewModel::onPhoneChange,
                label = { Text("手机号") },
                placeholder = { Text("请输入 11 位手机号") },
                singleLine = true,
                shape = RoundedCornerShape(14.dp),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(Dimens.GapM))

            OutlinedTextField(
                value = state.password,
                onValueChange = viewModel::onPasswordChange,
                label = { Text("密码") },
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
                text = if (state.isSubmitting) "登录中…" else "登录",
                onClick = viewModel::login,
                enabled = !state.isSubmitting
            )

            Spacer(modifier = Modifier.height(Dimens.GapS))

            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                TextButton(onClick = onGoRegister) {
                    Text(
                        text = "还没有账号？立即注册",
                        style = MaterialTheme.typography.labelMedium,
                        color = WarmPrimary
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(Dimens.GapXl))

        DemoBanner(
            text = "演示账号：13800000001 / 123456。当前版本所有页面使用模拟数据。"
        )

        Spacer(modifier = Modifier.height(Dimens.GapL))

        Text(
            text = "家属只能查看本人主动授权的信息。未经授权，任何人看不到你的生活记录。",
            style = MaterialTheme.typography.bodySmall,
            color = InkFaint,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/** App 标志：暖色圆角方块 + 「伴」字，和桌面图标保持一致 */
@Composable
fun AppLogo(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .size(80.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(WarmPrimary),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "伴",
            style = MaterialTheme.typography.displaySmall,
            color = Color.White
        )
    }
}
