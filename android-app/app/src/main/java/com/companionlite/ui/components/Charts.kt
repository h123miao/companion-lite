package com.companionlite.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.SurfaceSunken
import com.companionlite.ui.theme.TrustMissingBg
import com.companionlite.ui.theme.WarmPrimary
import com.companionlite.ui.theme.WarmPrimaryLight

/**
 * 签到时间柱状图。
 *
 * values：已经归一化到 0f~1f 的柱高；**null 表示这一天没有数据**。
 * 关键设计：没有数据的那一天不画 0 高度的柱子，而是画一个灰色小块，
 * 让用户一眼看出"没收到数据"和"今天签到了"是两回事——这是本项目的核心表达。
 */
@Composable
fun TimeBarChart(
    values: List<Float?>,
    labels: List<String>,
    modifier: Modifier = Modifier,
    barColor: androidx.compose.ui.graphics.Color = WarmPrimaryLight
) {
    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(140.dp),
            verticalAlignment = Alignment.Bottom,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            values.forEach { value ->
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight(),
                    contentAlignment = Alignment.BottomCenter
                ) {
                    if (value == null) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(12.dp)
                                .clip(RoundedCornerShape(4.dp))
                                .background(TrustMissingBg)
                        )
                    } else {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .fillMaxHeight(value.coerceIn(0.08f, 1f))
                                .clip(RoundedCornerShape(topStart = 6.dp, topEnd = 6.dp))
                                .background(barColor)
                        )
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Row(modifier = Modifier.fillMaxWidth()) {
            labels.forEach { label ->
                Text(
                    text = label,
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.labelSmall,
                    color = InkFaint,
                    textAlign = TextAlign.Center
                )
            }
        }
        Spacer(modifier = Modifier.height(Dimens.GapM))
        ChartLegend()
    }
}

/** 图表图例：明确告诉用户柱子代表什么、灰块代表什么。 */
@Composable
fun ChartLegend() {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .width(14.dp)
                .height(8.dp)
                .clip(RoundedCornerShape(3.dp))
                .background(WarmPrimaryLight)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = "有记录",
            style = MaterialTheme.typography.bodySmall,
            color = InkSoft
        )
        Spacer(modifier = Modifier.width(Dimens.GapL))
        Box(
            modifier = Modifier
                .width(14.dp)
                .height(8.dp)
                .clip(RoundedCornerShape(3.dp))
                .background(TrustMissingBg)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = "没有收到数据",
            style = MaterialTheme.typography.bodySmall,
            color = InkSoft
        )
    }
}

/** 近 7 天活动数量柱状图 */
@Composable
fun CountBarChart(
    values: List<Int>,
    labels: List<String>,
    modifier: Modifier = Modifier
) {
    val max = (values.maxOrNull() ?: 1).coerceAtLeast(1)
    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(120.dp),
            verticalAlignment = Alignment.Bottom,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            values.forEach { value ->
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight(),
                    contentAlignment = Alignment.BottomCenter
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .fillMaxHeight((value.toFloat() / max).coerceIn(0.08f, 1f))
                            .clip(RoundedCornerShape(topStart = 6.dp, topEnd = 6.dp))
                            .background(WarmPrimary)
                    )
                }
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Row(modifier = Modifier.fillMaxWidth()) {
            labels.forEach { label ->
                Text(
                    text = label,
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.labelSmall,
                    color = InkFaint,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

/** 一条水平进度条（用于"本周签到率"这类展示） */
@Composable
fun ProgressBar(
    fraction: Float,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(10.dp)
            .clip(RoundedCornerShape(999.dp))
            .background(SurfaceSunken)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(fraction.coerceIn(0f, 1f))
                .fillMaxHeight()
                .clip(RoundedCornerShape(999.dp))
                .background(WarmPrimary)
        )
    }
}
