package com.companionlite.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/**
 * 只做浅色主题。
 * 原因：目标是中老年用户，深色模式在强光下反而看不清；
 * 而且只维护一套配色，四个人的页面风格才不会跑偏。
 */
private val CompanionColorScheme = lightColorScheme(
    primary = WarmPrimary,
    onPrimary = Color.White,
    primaryContainer = WarmContainer,
    onPrimaryContainer = OnWarmContainer,

    secondary = InkSoft,
    onSecondary = Color.White,
    secondaryContainer = SurfaceSunken,
    onSecondaryContainer = InkText,

    tertiary = TrustUser,
    onTertiary = Color.White,
    tertiaryContainer = TrustUserBg,
    onTertiaryContainer = TrustUser,

    background = CreamBackground,
    onBackground = InkText,
    surface = SurfaceWhite,
    onSurface = InkText,
    surfaceVariant = SurfaceSunken,
    onSurfaceVariant = InkSoft,

    outline = DividerSoft,
    outlineVariant = DividerSoft,

    error = TrustAlert,
    onError = Color.White,
    errorContainer = TrustAlertBg,
    onErrorContainer = TrustAlert,

    scrim = Color(0x66000000)
)

@Composable
fun CompanionLiteTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = CompanionColorScheme,
        typography = AppTypography,
        content = content
    )
}
