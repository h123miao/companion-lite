package com.companionlite.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.companionlite.data.model.ActivityRecord
import com.companionlite.data.model.DataTrustState
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.WarmContainer
import com.companionlite.ui.theme.WarmPrimary

/**
 * 一条活动记录的展示行（首页「最近活动」和历史时间线共用）。
 *
 * 展示规则：只有「不是本人主动填写」的数据才显示可信度标签，
 * 否则每条都挂一个"本人反馈"标签，界面会变得很吵。
 */
@Composable
fun ActivityRow(
    record: ActivityRecord,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = Dimens.GapM),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // 左侧时间
        Column(modifier = Modifier.width(66.dp)) {
            Text(
                text = String.format("%02d:%02d", record.time.hour, record.time.minute),
                style = MaterialTheme.typography.titleSmall,
                color = InkText,
                fontWeight = FontWeight.SemiBold
            )
            Text(
                text = record.source,
                style = MaterialTheme.typography.labelSmall,
                color = InkFaint
            )
        }

        Spacer(modifier = Modifier.width(Dimens.GapM))

        // 中间：类型 + 备注
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = record.type.label,
                style = MaterialTheme.typography.bodyLarge,
                color = InkText
            )
            if (record.note.isNotBlank()) {
                Text(
                    text = record.note,
                    style = MaterialTheme.typography.bodySmall,
                    color = InkSoft
                )
            }
        }

        if (record.trust != DataTrustState.USER_FEEDBACK &&
            record.trust != DataTrustState.NORMAL
        ) {
            TrustBadge(trust = record.trust)
        }
    }
}

/** 时间线上的一个圆点和竖线，用来串联一天的活动 */
@Composable
fun TimelineDot(
    modifier: Modifier = Modifier,
    filled: Boolean = true
) {
    Box(
        modifier = modifier.size(36.dp),
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .size(if (filled) 12.dp else 10.dp)
                .clip(CircleShape)
                .background(if (filled) WarmPrimary else WarmContainer)
        )
    }
}

/** 日期分组标题：例如「今天 · 11月26日」 */
@Composable
fun DateGroupHeader(
    primaryText: String,
    secondaryText: String,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(top = Dimens.GapL, bottom = Dimens.GapS),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Start
    ) {
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(999.dp))
                .background(WarmContainer)
                .padding(horizontal = 10.dp, vertical = 4.dp)
        ) {
            Text(
                text = primaryText,
                style = MaterialTheme.typography.labelMedium,
                color = WarmPrimary
            )
        }
        Spacer(modifier = Modifier.width(Dimens.GapS))
        Text(
            text = secondaryText,
            style = MaterialTheme.typography.bodySmall,
            color = InkFaint
        )
    }
}
