package com.companionlite.ui.screens.activity

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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.data.model.ActivityType
import com.companionlite.ui.components.ActivityRow
import com.companionlite.ui.components.AppTopBar
import com.companionlite.ui.components.EmptyHint
import com.companionlite.ui.components.PrimaryButton
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.components.SelectableChip
import com.companionlite.ui.components.SoftDivider
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.TrustAlert

/**
 * 活动记录页：起床 / 外出 / 回家 / 用餐 / 运动 / 休息 / 服药 / 其他。
 * 目标是"三步内记完"：点类型 → 备注（可跳过）→ 提交。
 */
@Composable
fun ActivityRecordScreen(
    onBack: () -> Unit,
    onSubmitted: () -> Unit,
    viewModel: ActivityRecordViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CreamBackground)
    ) {
        AppTopBar(title = "记录活动", onBack = onBack)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = Dimens.ScreenPadding)
                .padding(bottom = Dimens.GapXxl)
        ) {
            SectionCard(
                title = "做了什么？",
                trailing = {
                    Text(
                        text = "现在 " + state.currentTimeText,
                        style = MaterialTheme.typography.bodySmall,
                        color = InkFaint
                    )
                }
            ) {
                TwoColumnChips(
                    options = ActivityType.entries,
                    label = { it.label },
                    selected = state.type,
                    onSelect = viewModel::onTypeChange
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "备注（可以不填）") {
                OutlinedTextField(
                    value = state.note,
                    onValueChange = viewModel::onNoteChange,
                    placeholder = { Text("例如：去菜市场买菜") },
                    shape = RoundedCornerShape(14.dp),
                    minLines = 2,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            if (state.error != null) {
                Spacer(modifier = Modifier.height(Dimens.GapM))
                Text(
                    text = state.error.orEmpty(),
                    style = MaterialTheme.typography.bodyMedium,
                    color = TrustAlert
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            PrimaryButton(
                text = "保存这条记录",
                onClick = {
                    viewModel.submit()
                    onSubmitted()
                },
                enabled = state.type != null
            )

            Spacer(modifier = Modifier.height(Dimens.GapXl))

            SectionCard(title = "今天已记录 ${state.todayRecords.size} 条") {
                if (state.todayRecords.isEmpty()) {
                    EmptyHint(text = "今天还没有记录活动")
                } else {
                    state.todayRecords.forEachIndexed { index, record ->
                        ActivityRow(record = record)
                        if (index != state.todayRecords.lastIndex) {
                            SoftDivider()
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))
            Text(
                text = "备注里写下的内容只有你和已授权的家人能看到。",
                style = MaterialTheme.typography.bodySmall,
                color = InkSoft
            )
        }
    }
}

/** 两列等宽的可选按钮 */
@Composable
private fun <T> TwoColumnChips(
    options: List<T>,
    label: (T) -> String,
    selected: T?,
    onSelect: (T) -> Unit
) {
    val rows = options.chunked(2)
    Column {
        rows.forEachIndexed { rowIndex, rowItems ->
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
            if (rowIndex != rows.lastIndex) {
                Spacer(modifier = Modifier.height(Dimens.GapM))
            }
        }
    }
}
