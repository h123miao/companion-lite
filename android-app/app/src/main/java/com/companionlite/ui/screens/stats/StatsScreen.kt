package com.companionlite.ui.screens.stats

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
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.data.model.DataTrustState
import com.companionlite.ui.components.AppTopBar
import com.companionlite.ui.components.CountBarChart
import com.companionlite.ui.components.DemoBanner
import com.companionlite.ui.components.InfoRow
import com.companionlite.ui.components.NoticeBar
import com.companionlite.ui.components.ProgressBar
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.components.StatTile
import com.companionlite.ui.components.TimeBarChart
import com.companionlite.ui.components.TrustBadge
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.TrustWait
import com.companionlite.ui.theme.TrustWaitBg

/**
 * 生活规律统计页（模块 9）。
 * 图表只做"看得懂"的展示：一根柱子 = 一天；灰块 = 那天没有数据。
 * 不做复杂仪表盘，也不把缺失数据画成 0。
 */
@Composable
fun StatsScreen(
    onBack: () -> Unit,
    viewModel: StatsViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val baseline = state.baseline

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(CreamBackground)
    ) {
        AppTopBar(title = "生活规律", onBack = onBack)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = Dimens.ScreenPadding)
                .padding(bottom = Dimens.GapXxl)
        ) {
            DemoBanner()

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(
                title = "你的个人基线",
                trailing = { TrustBadge(trust = baseline.trust) }
            ) {
                Text(
                    text = "这些数字是根据你自己过去 " + baseline.validDays +
                        " 天的记录算出来的，不是拿全国统一标准来比较你。",
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkSoft
                )
                Spacer(modifier = Modifier.height(Dimens.GapM))
                InfoRow(label = "平时签到时间（中位数）", value = timeText(baseline))
                InfoRow(
                    label = "时间波动范围",
                    value = "±" + baseline.spreadMinutes + " 分钟"
                )
                InfoRow(
                    label = "最早 / 最晚签到",
                    value = (baseline.earliest?.let { formatTime(it) } ?: "--") +
                        " / " + (baseline.latest?.let { formatTime(it) } ?: "--")
                )
                InfoRow(
                    label = "平均每天活动记录",
                    value = String.format("%.1f", baseline.dailyActivityAvg) + " 条"
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "近 14 天签到时间") {
                TimeBarChart(
                    values = state.checkInBarValues,
                    labels = state.checkInBarLabels
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            Row(modifier = Modifier.fillMaxWidth()) {
                StatTile(
                    value = "${(state.checkInRate * 100).toInt()}%",
                    label = "近 14 天签到率",
                    modifier = Modifier.weight(1f)
                )
                Spacer(modifier = Modifier.width(Dimens.GapM))
                StatTile(
                    value = "${baseline.validDays} 天",
                    label = "有效数据天数",
                    modifier = Modifier.weight(1f)
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "近 7 天活动记录") {
                CountBarChart(
                    values = state.activityCounts,
                    labels = state.activityLabels
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "数据可信度说明") {
                Text(
                    text = "系统在看你的记录之前，会先检查数据本身是否可靠。",
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkSoft
                )
                Spacer(modifier = Modifier.height(Dimens.GapM))

                DataTrustRow(DataTrustState.NORMAL, "手表或手机已同步，数据完整")
                DataTrustRow(DataTrustState.MISSING, "没有收到预期数据，原因未知")
                DataTrustRow(DataTrustState.OFFLINE, "设备明确处于离线状态")
                DataTrustRow(DataTrustState.DELAYED, "数据还没同步完成")
                DataTrustRow(DataTrustState.USER_FEEDBACK, "你自己填写的记录")
                DataTrustRow(DataTrustState.INSUFFICIENT, "历史记录太少，系统不下结论")
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            SectionCard(title = "关怀事件") {
                InfoRow(label = "本周触发", value = "${state.careEventTotal} 次")
                InfoRow(label = "已处理完成", value = "${state.careEventHandled} 次")
                Spacer(modifier = Modifier.height(Dimens.GapM))
                ProgressBar(
                    fraction = if (state.careEventTotal == 0) {
                        0f
                    } else {
                        state.careEventHandled.toFloat() / state.careEventTotal.toFloat()
                    }
                )
                Spacer(modifier = Modifier.height(Dimens.GapS))
                Text(
                    text = "关怀事件只有在你本人确认后，才会通知已授权的家人。",
                    style = MaterialTheme.typography.bodySmall,
                    color = InkFaint
                )
            }

            Spacer(modifier = Modifier.height(Dimens.GapL))

            NoticeBar(
                text = "有效记录少于 7 天时，页面会显示「数据不足，暂不判断」，不会给出任何结论。",
                tint = TrustWait,
                background = TrustWaitBg
            )
        }
    }
}

/** 一条数据可信度说明 */
@Composable
private fun DataTrustRow(trust: DataTrustState, description: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
    ) {
        TrustBadge(trust = trust)
        Spacer(modifier = Modifier.width(Dimens.GapM))
        Text(
            text = description,
            style = MaterialTheme.typography.bodySmall,
            color = InkSoft,
            modifier = Modifier.weight(1f)
        )
    }
}

private fun formatTime(time: java.time.LocalTime): String =
    String.format("%d:%02d", time.hour, time.minute)

private fun timeText(baseline: com.companionlite.data.model.BaselineProfile): String {
    val median = baseline.medianCheckIn ?: return "暂无"
    return formatTime(median)
}
