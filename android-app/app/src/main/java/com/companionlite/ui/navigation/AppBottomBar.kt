package com.companionlite.ui.navigation

import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.dp
import com.companionlite.ui.theme.InkFaint
import com.companionlite.ui.theme.SurfaceWhite
import com.companionlite.ui.theme.WarmContainer
import com.companionlite.ui.theme.WarmPrimary

/**
 * 底部导航栏：只有 3 个一级页面（首页 / 记录 / 我的）。
 * 一级页面数量刻意控制在 3 个，中老年用户不容易迷路。
 */
@Composable
fun AppBottomBar(
    currentRoute: String?,
    onTabSelected: (TopLevelTab) -> Unit
) {
    NavigationBar(
        containerColor = SurfaceWhite,
        tonalElevation = 0.dp
    ) {
        TopLevelTab.entries.forEach { tab ->
            NavigationBarItem(
                selected = currentRoute == tab.route,
                onClick = { onTabSelected(tab) },
                icon = {
                    Icon(
                        imageVector = tab.icon,
                        contentDescription = tab.label
                    )
                },
                label = {
                    Text(
                        text = tab.label,
                        style = MaterialTheme.typography.labelMedium
                    )
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = WarmPrimary,
                    selectedTextColor = WarmPrimary,
                    indicatorColor = WarmContainer,
                    unselectedIconColor = InkFaint,
                    unselectedTextColor = InkFaint
                )
            )
        }
    }
}
