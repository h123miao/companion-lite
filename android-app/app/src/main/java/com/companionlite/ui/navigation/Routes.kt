package com.companionlite.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.ui.graphics.vector.ImageVector

/** 所有页面的路由名。加页面就在这里加一行。 */
object Routes {
    const val LOGIN = "login"
    const val REGISTER = "register"

    const val HOME = "home"
    const val CHECK_IN = "check_in"
    const val ACTIVITY = "activity"
    const val TIMELINE = "timeline"
    const val STATS = "stats"
    const val PROFILE = "profile"
}

/** 底部三个一级页面（只有这三个页面显示底部导航栏） */
enum class TopLevelTab(
    val route: String,
    val label: String,
    val icon: ImageVector
) {
    HOME(Routes.HOME, "首页", Icons.Filled.Home),
    TIMELINE(Routes.TIMELINE, "记录", Icons.Filled.DateRange),
    PROFILE(Routes.PROFILE, "我的", Icons.Filled.Person)
}
