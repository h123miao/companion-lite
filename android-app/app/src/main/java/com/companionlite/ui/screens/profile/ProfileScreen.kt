package com.companionlite.ui.screens.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.data.model.DataTrustState
import com.companionlite.ui.components.InfoRow
import com.companionlite.ui.components.NoticeBar
import com.companionlite.ui.components.SecondaryButton
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.components.SoftDivider
import com.companionlite.ui.components.TrustBadge
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.SurfaceSunken
import com.companionlite.ui.theme.SurfaceWhite
import com.companionlite.ui.theme.TrustWait
import com.companionlite.ui.theme.TrustWaitBg
import com.companionlite.ui.theme.WarmContainer
import com.companionlite.ui.theme.WarmPrimary

/**
 * 「我的」页面：个人资料 + 家庭成员与授权 + 隐私说明 + 退出登录。
 * 家庭绑定用邀请码完成，邀请码由后端生成（成员 C）。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onLogout: () -> Unit,
    viewModel: ProfileViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    if (state.showLogoutConfirm) {
        AlertDialog(
            onDismissRequest = viewModel::onDismissLogout,
            containerColor = SurfaceWhite,
            shape = RoundedCornerShape(24.dp),
            title = { Text("确认退出登录？", style = MaterialTheme.typography.titleLarge) },
            text = { Text("退出后需要重新输入用户名和密码。", style = MaterialTheme.typography.bodyMedium) },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.onDismissLogout()
                    onLogout()
                }) {
                    Text("退出", color = WarmPrimary)
                }
            },
            dismissButton = {
                TextButton(onClick = viewModel::onDismissLogout) {
                    Text("再想想", color = InkSoft)
                }
            }
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CreamBackground)
            .statusBarsPadding()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = Dimens.ScreenPadding)
            .padding(top = Dimens.GapL, bottom = Dimens.GapXl)
    ) {
        Text(
            text = "我的",
            style = MaterialTheme.typography.headlineSmall,
            color = InkText
        )

        Spacer(modifier = Modifier.height(Dimens.GapL))

        // 个人信息
        SectionCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(WarmContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = state.user.name.take(1),
                        style = MaterialTheme.typography.headlineSmall,
                        color = WarmPrimary
                    )
                }
                Spacer(modifier = Modifier.width(Dimens.GapL))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = state.user.name,
                        style = MaterialTheme.typography.titleLarge,
                        color = InkText,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(Dimens.GapXs))
                    Text(
                        text = state.user.phone + " · " + state.user.roleLabel,
                        style = MaterialTheme.typography.bodyMedium,
                        color = InkSoft
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(Dimens.GapL))

        // 家庭绑定与授权
        SectionCard(
            title = "家人",
            trailing = { TrustBadge(trust = DataTrustState.USER_FEEDBACK) }
        ) {
            Text(
                text = "家庭邀请码",
                style = MaterialTheme.typography.bodyMedium,
                color = InkSoft
            )
            Spacer(modifier = Modifier.height(Dimens.GapXs))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(SurfaceSunken)
                    .padding(vertical = Dimens.GapL),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = state.user.inviteCode,
                    style = MaterialTheme.typography.headlineSmall,
                    color = WarmPrimary,
                    fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.height(Dimens.GapS))
            Text(
                text = "把邀请码告诉家人，他们申请后需要你在这里同意才能看到你的情况。",
                style = MaterialTheme.typography.bodySmall,
                color = InkFaint
            )

            Spacer(modifier = Modifier.height(Dimens.GapL))
            SoftDivider()
            Spacer(modifier = Modifier.height(Dimens.GapS))

            state.family.forEach { member ->
                InfoRow(
                    label = member.name + "（" + member.relation + "）",
                    value = if (member.canViewStatus) "可查看状态" else "未授权"
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapS))

            SwitchRow(
                title = "允许家人查看我的状态",
                subtitle = "关闭后家人看不到签到和活动记录",
                checked = state.shareStatusToFamily,
                onCheckedChange = viewModel::onShareStatusChange
            )
            SwitchRow(
                title = "允许家人接收关怀提醒",
                subtitle = "只有你确认后，才会通知家人",
                checked = state.allowFamilyAlert,
                onCheckedChange = viewModel::onAllowAlertChange
            )
        }

        Spacer(modifier = Modifier.height(Dimens.GapL))

        SectionCard(title = "隐私说明") {
            Text(
                text = "1. 未经你授权，家人看不到你的任何记录。\n" +
                    "2. 撤销授权后，后端会立即阻止家人的查询请求。\n" +
                    "3. 系统不会把「没有收到数据」直接判断为异常。\n" +
                    "4. 本应用不做医疗诊断，也不能预测疾病。",
                style = MaterialTheme.typography.bodyMedium,
                color = InkSoft
            )
        }

        Spacer(modifier = Modifier.height(Dimens.GapL))

        SectionCard(title = "关于") {
            InfoRow(label = "版本", value = "0.1.0（初赛原型）")
            InfoRow(label = "数据来源", value = "演示数据 + 本人填写")
            Spacer(modifier = Modifier.height(Dimens.GapM))
            NoticeBar(
                text = "当前版本所有页面使用模拟数据，所有时间与记录均为演示用途。",
                tint = TrustWait,
                background = TrustWaitBg
            )
        }

        Spacer(modifier = Modifier.height(Dimens.GapXl))

        SecondaryButton(
            text = "退出登录",
            onClick = viewModel::onRequestLogout
        )

        Spacer(modifier = Modifier.height(Dimens.GapM))
        Text(
            text = "伴行·时序 · 让关心更及时，也更有分寸",
            style = MaterialTheme.typography.bodySmall,
            color = InkFaint,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/** 带说明文字的开关行 */
@Composable
private fun SwitchRow(
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = Dimens.GapS),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
                color = InkText
            )
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = InkFaint
            )
        }
        Spacer(modifier = Modifier.width(Dimens.GapM))
        Switch(checked = checked, onCheckedChange = onCheckedChange)
    }
}
