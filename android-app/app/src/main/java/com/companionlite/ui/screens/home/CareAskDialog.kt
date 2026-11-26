package com.companionlite.ui.screens.home

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.companionlite.data.model.FeedbackType
import com.companionlite.ui.theme.InkSoft
import com.companionlite.ui.theme.InkText
import com.companionlite.ui.theme.SurfaceWhite
import com.companionlite.ui.theme.WarmPrimary

/**
 * 主动关怀询问弹窗（模块 7）。
 *
 * 这是本项目最关键的交互：系统发现记录变化后，**先问本人**，
 * 而不是直接告诉家属"出事了"。文案里不能出现"异常""危险"这类判断。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CareAskDialog(
    reason: String,
    onAnswer: (FeedbackType) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = SurfaceWhite,
        shape = RoundedCornerShape(24.dp),
        title = {
            Text(
                text = "想确认一下你现在的情况",
                style = MaterialTheme.typography.titleLarge,
                color = InkText
            )
        },
        text = {
            Column {
                Text(
                    text = reason,
                    style = MaterialTheme.typography.bodyMedium,
                    color = InkSoft
                )
                Spacer(modifier = Modifier.height(16.dp))
                FeedbackType.entries.forEach { feedback ->
                    OutlinedButton(
                        onClick = { onAnswer(feedback) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 8.dp),
                        shape = RoundedCornerShape(14.dp)
                    ) {
                        Text(
                            text = feedback.label,
                            style = MaterialTheme.typography.labelLarge,
                            color = WarmPrimary
                        )
                    }
                }
            }
        },
        confirmButton = {}
    )
}
