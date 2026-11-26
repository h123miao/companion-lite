package com.companionlite.ui.screens.timeline

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.ui.components.DateGroupHeader
import com.companionlite.ui.components.DemoBanner
import com.companionlite.ui.components.PrimaryButton
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.components.SoftDivider
import com.companionlite.ui.components.TrustBadge
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.WarmPrimary

/**
 * 历史记录时间线（一级页面「记录」）。
 * 一天一组，签到和活动都在里面，没有收到数据的那天也会显示出来。
 */
@Composable
fun TimelineScreen(
    onAddActivity: () -> Unit,
    viewModel: TimelineViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

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
            text = "生活记录",
            style = MaterialTheme.typography.headlineSmall,
            color = InkText
        )
        Spacer(modifier = Modifier.height(Dimens.GapXs))
        Text(
            text = "近 14 天 · 签到 ${state.checkInDays} 天 · 活动 ${state.activityCount} 条",
            style = MaterialTheme.typography.bodyMedium,
            color = InkSoft
        )

        Spacer(modifier = Modifier.height(Dimens.GapL))
        DemoBanner()
        Spacer(modifier = Modifier.height(Dimens.GapL))

        // 筛选
        Row(modifier = Modifier.fillMaxWidth()) {
            TimelineFilter.entries.forEachIndexed { index, filter ->
                FilterPill(
                    text = filter.label,
                    selected = state.filter == filter,
                    onClick = { viewModel.onFilterChange(filter) },
                    modifier = Modifier.weight(1f)
                )
                if (index != TimelineFilter.entries.lastIndex) {
                    Spacer(modifier = Modifier.width(Dimens.GapS))
                }
            }
        }

        Spacer(modifier = Modifier.height(Dimens.GapS))

        if (state.groups.isEmpty()) {
            Spacer(modifier = Modifier.height(Dimens.GapXl))
            Text(
                text = "还没有记录",
                style = MaterialTheme.typography.bodyMedium,
                color = InkFaint,
                modifier = Modifier.fillMaxWidth()
            )
        }

        state.groups.forEach { group ->
            DateGroupHeader(
                primaryText = group.dayLabel,
                secondaryText = group.dateLabel
            )
            SectionCard {
                group.entries.forEachIndexed { index, entry ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = Dimens.GapS),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = entry.timeText,
                            style = MaterialTheme.typography.titleSmall,
                            color = InkFaint,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.width(64.dp)
                        )
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = entry.title,
                                style = MaterialTheme.typography.bodyLarge,
                                color = InkText
                            )
                            Text(
                                text = entry.subtitle,
                                style = MaterialTheme.typography.bodySmall,
                                color = InkSoft
                            )
                        }
                        if (entry.kind == TimelineFilter.CHECK_IN) {
                            TrustBadge(trust = entry.trust)
                        }
                    }
                    if (index != group.entries.lastIndex) {
                        SoftDivider()
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(Dimens.GapXl))

        PrimaryButton(text = "记一笔活动", onClick = onAddActivity)
    }
}

/** 时间线上的筛选胶囊 */
@Composable
private fun FilterPill(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .height(Dimens.MinTouchHeight)
            .background(
                color = if (selected) WarmPrimary else CreamBackground,
                shape = RoundedCornerShape(999.dp)
            )
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = if (selected) Color.White else InkSoft
        )
    }
}
