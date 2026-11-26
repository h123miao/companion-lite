package com.companionlite.ui.screens.checkin

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
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.data.model.CheckInStatus
import com.companionlite.data.model.MoodType
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
 * 每日签到页（模块 2 的一部分）。
 *
 * 设计取舍：把「身体感觉」和「心情」放在同一页，分两个区块，
 * 而不是拆成两页。中老年用户少点一次是一次，一次填写两分钟就完成。
 */
@Composable
fun CheckInScreen(
    onBack: () -> Unit,
    onSubmitted: () -> Unit,
    viewModel: CheckInViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(state.submitted) {
        if (state.submitted) {
            onSubmitted()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CreamBackground)
    ) {
        AppTopBar(title = "每日签到", onBack = onBack)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = Dimens.ScreenPadding)
                .padding(bottom = Dimens.GapXxl)
        ) {
            SectionCard(title = "今天身体感觉怎么样？") {
                TwoColumnChips(
                    options = CheckInStatus.entries,
                    label = { it.label },
                    selected = state.status,
                    onSelect = viewModel::onStatusChange
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "今天心情怎么样？") {
                TwoColumnChips(
                    options = MoodType.entries.filter { it != MoodType.UNKNOWN },
                    label = { it.label },
                    selected = state.mood,
                    onSelect = viewModel::onMoodChange
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "想补充点什么吗？") {
                OutlinedTextField(
                    value = state.note,
                    onValueChange = viewModel::onNoteChange,
                    placeholder = { Text("例如：昨晚没睡好，今天起晚了") },
                    shape = RoundedCornerShape(14.dp),
                    minLines = 3,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "希望家人联系我",
                            style = MaterialTheme.typography.titleSmall,
                            color = InkText
                        )
                        Spacer(modifier = Modifier.height(Dimens.GapXs))
                        Text(
                            text = "打开后会通知已授权的家人，由他们来联系你",
                            style = MaterialTheme.typography.bodySmall,
                            color = InkSoft
                        )
                    }
                    Spacer(modifier = Modifier.width(Dimens.GapM))
                    Switch(
                        checked = state.wantFamilyCall,
                        onCheckedChange = viewModel::onWantFamilyCallChange
                    )
                }
            }

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
                text = "提交签到",
                onClick = viewModel::submit,
                enabled = state.status != null
            )

            Spacer(modifier = Modifier.height(Dimens.GapM))

            Text(
                text = "签到记录只有你和已授权的家人能看到。",
                style = MaterialTheme.typography.bodySmall,
                color = InkSoft
            )
        }
    }
}

/** 两列等宽的可选按钮，避免使用实验性的 FlowRow */
@Composable
private fun <T> TwoColumnChips(
    options: List<T>,
    label: (T) -> String,
    selected: T?,
    onSelect: (T) -> Unit
) {
    Column {
        options.chunked(2).forEachIndexed { rowIndex, rowItems ->
            Row(modifier = Modifier.fillMaxWidth()) {
                rowItems.forEachIndexed { index, item ->
                    SelectableChip(
                        text = label(item),
                        selected = item == selected,
                        onClick = { onSelect(item) },
                        modifier = Modifier.weight(1f)
                    )
                    if (index == 0) {
                        Spacer(modifier = Modifier.width(Dimens.GapM))
                    }
                }
                if (rowItems.size == 1) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
            if (rowIndex != options.chunked(2).lastIndex) {
                Spacer(modifier = Modifier.height(Dimens.GapM))
            }
        }
    }
}
