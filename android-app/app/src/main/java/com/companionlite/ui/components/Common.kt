package com.companionlite.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.companionlite.data.model.DataTrustState
import com.companionlite.ui.theme.CreamBackground
import com.companionlite.ui.theme.Dimens
import com.companionlite.ui.theme.DividerSoft
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.OnWarmContainer
import com.companionlite.ui.theme.SurfaceSunken
import com.companionlite.ui.theme.SurfaceWhite
import com.companionlite.ui.theme.TrustAlert
import com.companionlite.ui.theme.TrustAlertBg
import com.companionlite.ui.theme.TrustMissing
import com.companionlite.ui.theme.TrustMissingBg
import com.companionlite.ui.theme.TrustNormal
import com.companionlite.ui.theme.TrustNormalBg
import com.companionlite.ui.theme.TrustUser
import com.companionlite.ui.theme.TrustUserBg
import com.companionlite.ui.theme.TrustWait
import com.companionlite.ui.theme.TrustWaitBg
import com.companionlite.ui.theme.WarmContainer
import com.companionlite.ui.theme.WarmPrimary

/** 页面顶栏：所有二级页面统一用它，返回键在左边。 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppTopBar(
    title: String,
    onBack: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = { Text(text = title, style = MaterialTheme.typography.titleLarge) },
        navigationIcon = {
            if (onBack != null) {
                IconButton(onClick = onBack) {
                    Icon(imageVector = Icons.Filled.ArrowBack, contentDescription = "返回")
                }
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = CreamBackground,
            titleContentColor = InkText,
            navigationIconContentColor = InkText,
            actionIconContentColor = InkText
        )
    )
}

/** 卡片容器：白底 + 细边 + 圆角，全 App 只用这一种卡片。 */
@Composable
fun SectionCard(
    modifier: Modifier = Modifier,
    title: String? = null,
    trailing: (@Composable () -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(Dimens.CardCorner),
        color = SurfaceWhite,
        border = BorderStroke(1.dp, DividerSoft)
    ) {
        Column(modifier = Modifier.padding(Dimens.CardPadding)) {
            if (title != null) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleSmall,
                        color = InkText,
                        modifier = Modifier.weight(1f)
                    )
                    trailing?.invoke()
                }
                Spacer(modifier = Modifier.height(Dimens.GapM))
            }
            content()
        }
    }
}

/** 主按钮：高度至少 56dp，够大的点击区域。 */
@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier
            .fillMaxWidth()
            .heightIn(min = Dimens.ButtonHeight),
        shape = RoundedCornerShape(16.dp),
        contentPadding = PaddingValues(horizontal = 24.dp, vertical = 14.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = WarmPrimary,
            contentColor = Color.White,
            disabledContainerColor = SurfaceSunken,
            disabledContentColor = InkFaint
        )
    ) {
        Text(text = text, style = MaterialTheme.typography.labelLarge)
    }
}

/** 次要按钮：描边样式，用于"稍后再说""查看全部"这类操作。 */
@Composable
fun SecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    OutlinedButton(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier
            .fillMaxWidth()
            .heightIn(min = Dimens.ButtonHeight),
        shape = RoundedCornerShape(16.dp),
        contentPadding = PaddingValues(horizontal = 24.dp, vertical = 14.dp),
        border = BorderStroke(1.5.dp, WarmPrimary)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelLarge,
            color = WarmPrimary
        )
    }
}

/** 可选择的胶囊按钮（签到状态、心情、活动类型都用它）。 */
@Composable
fun SelectableChip(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val background = if (selected) WarmContainer else SurfaceWhite
    val borderColor = if (selected) WarmPrimary else DividerSoft
    val textColor = if (selected) OnWarmContainer else InkText
    Box(
        modifier = modifier
            .heightIn(min = 52.dp)
            .clip(RoundedCornerShape(Dimens.ChipCorner))
            .background(background)
            .border(1.5.dp, borderColor, RoundedCornerShape(Dimens.ChipCorner))
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            color = textColor,
            textAlign = TextAlign.Center
        )
    }
}

/** 数据可信度对应的一组颜色（前景、背景）。 */
fun trustColors(trust: DataTrustState): Pair<Color, Color> = when (trust) {
    DataTrustState.NORMAL -> TrustNormal to TrustNormalBg
    DataTrustState.USER_FEEDBACK -> TrustUser to TrustUserBg
    DataTrustState.DELAYED -> TrustWait to TrustWaitBg
    DataTrustState.MISSING -> TrustMissing to TrustMissingBg
    DataTrustState.OFFLINE -> TrustMissing to TrustMissingBg
    DataTrustState.INSUFFICIENT -> TrustMissing to TrustMissingBg
}

/** 信任状态标签：全 App 统一展示"这条数据从哪来、可不可信"。 */
@Composable
fun TrustBadge(
    trust: DataTrustState,
    modifier: Modifier = Modifier
) {
    val (foreground, background) = trustColors(trust)
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(Dimens.ChipCorner))
            .background(background)
            .padding(horizontal = 10.dp, vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(foreground)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = trust.label,
            style = MaterialTheme.typography.labelSmall,
            color = foreground
        )
    }
}

/** 演示数据横幅：只要有模拟数据，这个横幅就必须在。 */
@Composable
fun DemoBanner(
    text: String = "演示数据：本页记录为模拟数据，不是真实设备采集。"
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(TrustWaitBg)
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Filled.Info,
            contentDescription = null,
            tint = TrustWait,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = TrustWait
        )
    }
}

/** 一行「标题 - 数值」 */
@Composable
fun InfoRow(
    label: String,
    value: String,
    valueColor: Color = InkText
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = InkSoft
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = valueColor,
            fontWeight = FontWeight.Medium,
            textAlign = TextAlign.End,
            modifier = Modifier.weight(1f)
        )
    }
}

/** 数字小卡：统计页用 */
@Composable
fun StatTile(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
    accent: Color = WarmPrimary
) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(SurfaceSunken)
            .padding(horizontal = 14.dp, vertical = 12.dp)
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            color = accent
        )
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = InkSoft
        )
    }
}

/** 空状态 / 提示文字 */
@Composable
fun EmptyHint(text: String, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 20.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = InkFaint,
            textAlign = TextAlign.Center
        )
    }
}

/** 细分隔线 */
@Composable
fun SoftDivider(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(1.dp)
            .background(DividerSoft)
    )
}

/** 带感叹号的提醒条：用于"数据缺失""需要关注"，措辞必须是"待确认"而不是"危险"。 */
@Composable
fun NoticeBar(
    text: String,
    modifier: Modifier = Modifier,
    tint: Color = TrustAlert,
    background: Color = TrustAlertBg
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(background)
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Filled.Info,
            contentDescription = null,
            tint = tint,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = tint
        )
    }
}

/** 分组标题 */
@Composable
fun SectionTitle(text: String, modifier: Modifier = Modifier) {
    Text(
        text = text,
        style = MaterialTheme.typography.titleMedium,
        color = InkText,
        modifier = modifier.padding(bottom = Dimens.GapS)
    )
}

/** 横向并排的两个按钮之间的间距辅助 */
@Composable
fun RowGap() {
    Spacer(modifier = Modifier.width(Dimens.GapM))
}

/** 纵向间距 */
@Composable
fun VGap(height: androidx.compose.ui.unit.Dp = Dimens.GapL) {
    Spacer(modifier = Modifier.height(height))
}

/** 一行等宽排列的若干元素（用于 2 列/3 列网格，避免使用实验性的 FlowRow） */
@Composable
fun EqualRow(
    modifier: Modifier = Modifier,
    spacing: androidx.compose.ui.unit.Dp = Dimens.GapM,
    content: @Composable RowScope.() -> Unit
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(spacing),
        content = content
    )
}
