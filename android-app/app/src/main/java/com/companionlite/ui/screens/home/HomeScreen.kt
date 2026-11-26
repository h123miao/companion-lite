package com.companionlite.ui.screens.home

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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.companionlite.data.model.DailyCheckIn
import com.companionlite.data.model.DataTrustState
import com.companionlite.data.model.FeedbackType
import com.companionlite.ui.components.ActivityRow
import com.companionlite.ui.components.DemoBanner
import com.companionlite.ui.components.InfoRow
import com.companionlite.ui.components.PrimaryButton
import com.companionlite.ui.components.SectionCard
import com.companionlite.ui.components.SoftDivider
import com.companionlite.ui.components.StatTile
import com.companionlite.ui.components.TimeBarChart
import com.companionlite.ui.components.TrustBadge
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.SurfaceWhite
import com.companionlite.ui.theme.TrustWait
import com.companionlite.ui.theme.TrustWaitBg
import com.companionlite.ui.theme.WarmContainer
import com.companionlite.ui.theme.WarmPrimary

/**
 * 本人端首页（成员 A 的核心页面，答辩演示从这里开始）。
 *
 * 一屏之内必须能看懂三件事：
 *   1. 今天有没有签到（以及"没收到数据"和"没活动"的区别）
 *   2. 系统现在想问我什么（主动关怀）
 *   3. 我最近的生活规律有没有变化
 */
@Composable
fun HomeScreen(
    onCheckIn: () -> Unit,
    onAddActivity: () -> Unit,
    onOpenStats: () -> Unit,
    onOpenTimeline: () -> Unit,
    viewModel: HomeViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val careEvent = state.careEvent

    // 进入首页时，如果有一个待确认的关怀事件，就弹出主动询问
    LaunchedEffect(Unit) {
        viewModel.openCareDialog()
    }

    if (state.careDialogVisible && careEvent != null) {
        CareAskDialog(
            reason = careEvent.reason,
            onAnswer = viewModel::answerCareEvent,
            onDismiss = viewModel::dismissCareDialog
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
        // ---------- 顶部问候 ----------
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "${state.greeting}，${state.userName}",
                    style = MaterialTheme.typography.headlineSmall,
                    color = InkText
                )
                Spacer(modifier = Modifier.height(Dimens.GapXs))
                Text(
                    text = state.dateText,
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkSoft
                )
            }
            Box(
                modifier = Modifier
                    .size(52.dp)
                    .clip(CircleShape)
                    .background(WarmContainer),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = state.userName.take(1),
                    style = MaterialTheme.typography.titleLarge,
                    color = WarmPrimary
                )
            }
        }

        Spacer(modifier = Modifier.height(Dimens.GapL))
        DemoBanner()
        Spacer(modifier = Modifier.height(Dimens.GapL))

        // ---------- 今天的状态 ----------
        TodayStatusCard(
            todayCheckIn = state.todayCheckIn,
            onCheckIn = onCheckIn
        )

        // ---------- 主动关怀：待确认 ----------
        if (careEvent != null) {
            Spacer(modifier = Modifier.height(Dimens.GapL))
            CarePendingCard(
                title = "有一件事想和你确认",
                reason = careEvent.reason,
                onOpen = viewModel::openCareDialog
            )
        }

        // ---------- 主动关怀：本人已经回答 ----------
        val answered = state.answeredFeedback
        if (answered != null) {
            Spacer(modifier = Modifier.height(Dimens.GapL))
            CareAnsweredCard(feedback = answered)
        }

        // ---------- 快捷操作 ----------
        Spacer(modifier = Modifier.height(Dimens.GapL))
        Row(modifier = Modifier.fillMaxWidth()) {
            QuickAction(
                title = "每日签到",
                hint = "报个平安",
                onClick = onCheckIn,
                modifier = Modifier.weight(1f)
            )
            Spacer(modifier = Modifier.width(Dimens.GapM))
            QuickAction(
                title = "记一笔活动",
                hint = "外出 / 用餐",
                onClick = onAddActivity,
                modifier = Modifier.weight(1f)
            )
        }

        // ---------- 最近活动 ----------
        Spacer(modifier = Modifier.height(Dimens.GapL))
        SectionCard(
            title = "最近活动",
            trailing = {
                TextButton(onClick = onOpenTimeline) {
                    Text(
                        text = "全部记录",
                        style = MaterialTheme.typography.labelMedium,
                        color = WarmPrimary
                    )
                }
            }
        ) {
            if (state.recentActivities.isEmpty()) {
                Text(
                    text = "今天还没有记录活动",
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkFaint
                )
            } else {
                state.recentActivities.forEachIndexed { index, record ->
                    ActivityRow(record = record)
                    if (index != state.recentActivities.lastIndex) {
                        SoftDivider()
                    }
                }
            }
        }

        // ---------- 我的规律 ----------
        Spacer(modifier = Modifier.height(Dimens.GapL))
        SectionCard(
            title = "作息规律（近 7 天）",
            trailing = { TrustBadge(trust = state.baseline.trust) }
        ) {
            Text(
                text = "你平时大约 " + timeText(state.baseline.medianCheckIn) +
                    " 签到，前后浮动约 " + state.baseline.spreadMinutes + " 分钟。",
                style = MaterialTheme.typography.bodyMedium,
                color = InkSoft
            )
            Spacer(modifier = Modifier.height(Dimens.GapL))

            CheckInMiniChart(checkIns = state.recentCheckIns)

            Spacer(modifier = Modifier.height(Dimens.GapL))
            StatTile(
                value = "${state.baseline.validDays} 天",
                label = "可用于判断的有效记录",
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(Dimens.GapS))
            Text(
                text = "灰色块表示那天没有收到记录。没有记录不等于发生了什么事，系统不会据此下结论。",
                style = MaterialTheme.typography.bodySmall,
                color = InkFaint
            )
            Spacer(modifier = Modifier.height(Dimens.GapS))
            TextButton(
                onClick = onOpenStats,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "查看生活规律详情",
                    style = MaterialTheme.typography.labelMedium,
                    color = WarmPrimary
                )
            }
        }

        Spacer(modifier = Modifier.height(Dimens.GapXl))
        Text(
            text = "伴行·时序 v0.1 · 本人端",
            style = MaterialTheme.typography.labelSmall,
            color = InkFaint,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/** 今天有没有签到 */
@Composable
private fun TodayStatusCard(
    todayCheckIn: DailyCheckIn?,
    onCheckIn: () -> Unit
) {
    if (todayCheckIn != null) {
        SectionCard(
            title = "今天的状态",
            trailing = { TrustBadge(trust = DataTrustState.USER_FEEDBACK) }
        ) {
            InfoRow(label = "签到时间", value = timeText(todayCheckIn.time))
            InfoRow(label = "身体感觉", value = todayCheckIn.status?.label ?: "未填写")
            InfoRow(label = "心情", value = todayCheckIn.mood?.label ?: "未选择")
            if (todayCheckIn.note.isNotBlank()) {
                InfoRow(label = "备注", value = todayCheckIn.note)
            }
        }
    } else {
        SectionCard(
            title = "今天的状态",
            trailing = { TrustBadge(trust = DataTrustState.MISSING) }
        ) {
            Text(
                text = "今天还没有收到你的签到记录",
                style = MaterialTheme.typography.titleMedium,
                color = InkText
            )
            Spacer(modifier = Modifier.height(Dimens.GapS))
            Text(
                text = "可能只是今天起得晚，或者还没来得及点。签到只要 10 秒钟。",
                style = MaterialTheme.typography.bodyMedium,
                color = InkSoft
            )
            Spacer(modifier = Modifier.height(Dimens.GapL))
            PrimaryButton(text = "现在签到", onClick = onCheckIn)
        }
    }
}

/** 有待确认的关怀事件 */
@Composable
private fun CarePendingCard(
    title: String,
    reason: String,
    onOpen: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(Dimens.CardCorner))
            .clickable(onClick = onOpen),
        shape = RoundedCornerShape(Dimens.CardCorner),
        color = TrustWaitBg
    ) {
        Column(modifier = Modifier.padding(Dimens.CardPadding)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = InkText,
                    modifier = Modifier.weight(1f)
                )
                TrustBadge(trust = DataTrustState.MISSING)
            }
            Spacer(modifier = Modifier.height(Dimens.GapS))
            Text(
                text = reason,
                style = MaterialTheme.typography.bodyMedium,
                color = InkSoft
            )
            Spacer(modifier = Modifier.height(Dimens.GapM))
            Text(
                text = "点这里回答 ›",
                style = MaterialTheme.typography.labelMedium,
                color = TrustWait
            )
        }
    }
}

/** 本人回答之后，事件状态的变化 */
@Composable
private fun CareAnsweredCard(feedback: FeedbackType) {
    SectionCard(
        title = "关怀事件已更新",
        trailing = {
            TrustBadgeForAnswered(feedback)
        }
    ) {
        Text(
            text = "你选择了「${feedback.label}」，这条关怀事件的状态已经更新。",
            style = MaterialTheme.typography.bodyMedium,
            color = InkSoft
        )
        Spacer(modifier = Modifier.height(Dimens.GapS))
        Text(
            text = when (feedback) {
                FeedbackType.WANT_CALL -> "根据你的选择，已通知已授权的家人，等待对方联系你。"
                FeedbackType.UNWELL -> "已记录你的身体情况。如果持续不舒服，建议联系家人或就医。"
                FeedbackType.NO_ANSWER -> "你选择了暂时不回答，系统不会通知任何人。"
                else -> "系统不会通知家属，你今天的信息仍然只有你自己能看到。"
            },
            style = MaterialTheme.typography.bodyMedium,
            color = InkText
        )
    }
}

@Composable
private fun TrustBadgeForAnswered(feedback: FeedbackType) {
    if (feedback == FeedbackType.WANT_CALL || feedback == FeedbackType.UNWELL) {
        TrustBadge(trust = DataTrustState.MISSING)
    } else {
        TrustBadge(trust = DataTrustState.NORMAL)
    }
}

/** 快捷操作方块 */
@Composable
private fun QuickAction(
    title: String,
    hint: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .clip(RoundedCornerShape(Dimens.CardCorner))
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(Dimens.CardCorner),
        color = SurfaceWhite
    ) {
        Column(modifier = Modifier.padding(Dimens.CardPadding)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = WarmPrimary,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(Dimens.GapXs))
            Text(
                text = hint,
                style = MaterialTheme.typography.bodySmall,
                color = InkSoft
            )
        }
    }
}

/** 近 7 天签到时间小图 */
@Composable
private fun CheckInMiniChart(checkIns: List<DailyCheckIn>) {
    val startMinute = 6 * 60
    val spanMinute = 6 * 60f
    val values: List<Float?> = checkIns.map { checkIn ->
        checkIn.time?.let { time ->
            val minute = time.hour * 60 + time.minute
            ((minute - startMinute).toFloat() / spanMinute).coerceIn(0.05f, 1f)
        }
    }
    val labels: List<String> = checkIns.map { "${it.date.dayOfMonth}日" }
    Column {
        TimeBarChart(values = values, labels = labels)
    }
}

/** LocalTime -> "7:52"；null -> "暂无" */
private fun timeText(time: java.time.LocalTime?): String {
    if (time == null) return "暂无"
    return String.format("%d:%02d", time.hour, time.minute)
}
