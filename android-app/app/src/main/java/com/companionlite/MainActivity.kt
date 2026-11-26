package com.companionlite

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.companionlite.ui.navigation.AppNavHost
import com.companionlite.ui.theme.CompanionLiteTheme

/**
 * App 唯一的 Activity。
 * 整个界面用 Compose 写，入口只有这里，页面切换全部在 AppNavHost 里。
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CompanionLiteTheme {
                AppNavHost()
            }
        }
    }
}
