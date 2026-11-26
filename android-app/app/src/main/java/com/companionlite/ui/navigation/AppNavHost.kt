package com.companionlite.ui.navigation

import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.companionlite.ui.screens.activity.ActivityRecordScreen
import com.companionlite.ui.screens.auth.LoginScreen
import com.companionlite.ui.screens.auth.RegisterScreen
import com.companionlite.ui.screens.checkin.CheckInScreen
import com.companionlite.ui.screens.home.HomeScreen
import com.companionlite.ui.screens.profile.ProfileScreen
import com.companionlite.ui.screens.stats.StatsScreen
import com.companionlite.ui.screens.timeline.TimelineScreen
import com.companionlite.ui.theme.CreamBackground

/**
 * 全局导航。
 *
 * 结构：一个 NavHost 管所有页面，底部导航栏只在三个一级页面显示。
 * 注意：外层 Scaffold 的 contentWindowInsets 设为全 0，
 * 因为每个页面自己的 TopAppBar 已经处理了状态栏，否则顶部会被顶两次。
 */
@Composable
fun AppNavHost(
    navController: NavHostController = rememberNavController()
) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route
    val showBottomBar = TopLevelTab.entries.any { it.route == currentRoute }

    Scaffold(
        containerColor = CreamBackground,
        contentWindowInsets = WindowInsets(0, 0, 0, 0),
        bottomBar = {
            if (showBottomBar) {
                AppBottomBar(currentRoute = currentRoute) { tab ->
                    navController.switchTab(tab)
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Routes.LOGIN,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Routes.LOGIN) {
                LoginScreen(
                    onLoggedIn = {
                        navController.navigate(Routes.HOME) {
                            popUpTo(Routes.LOGIN) { inclusive = true }
                        }
                    },
                    onGoRegister = {
                        navController.navigate(Routes.REGISTER)
                    }
                )
            }

            composable(Routes.REGISTER) {
                RegisterScreen(
                    onBack = { navController.popBackStack() },
                    onRegistered = { navController.popBackStack() }
                )
            }

            composable(Routes.HOME) {
                HomeScreen(
                    onCheckIn = { navController.navigate(Routes.CHECK_IN) },
                    onAddActivity = { navController.navigate(Routes.ACTIVITY) },
                    onOpenStats = { navController.navigate(Routes.STATS) },
                    onOpenTimeline = { navController.switchTab(TopLevelTab.TIMELINE) }
                )
            }

            composable(Routes.CHECK_IN) {
                CheckInScreen(
                    onBack = { navController.popBackStack() },
                    onSubmitted = { navController.popBackStack() }
                )
            }

            composable(Routes.ACTIVITY) {
                ActivityRecordScreen(
                    onBack = { navController.popBackStack() },
                    onSubmitted = { navController.popBackStack() }
                )
            }

            composable(Routes.TIMELINE) {
                TimelineScreen(
                    onAddActivity = { navController.navigate(Routes.ACTIVITY) }
                )
            }

            composable(Routes.STATS) {
                StatsScreen(onBack = { navController.popBackStack() })
            }

            composable(Routes.PROFILE) {
                ProfileScreen(
                    onLogout = {
                        navController.navigate(Routes.LOGIN) {
                            popUpTo(navController.graph.id) { inclusive = true }
                        }
                    }
                )
            }
        }
    }
}

/** 切换底部 Tab：保留各 Tab 自己的滚动位置，返回键行为符合直觉。 */
private fun NavHostController.switchTab(tab: TopLevelTab) {
    navigate(tab.route) {
        popUpTo(graph.findStartDestination().id) { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}
