package com.companionlite.ui.theme

import androidx.compose.ui.unit.dp

/**
 * 统一的间距与尺寸。
 * 页面里不要写 13.dp、17.dp 这种零散数字，全部用这里的常量，四个人的界面才会一致。
 */
object Dimens {
    val ScreenPadding = 20.dp   // 页面左右边距
    val GapXs = 4.dp
    val GapS = 8.dp
    val GapM = 12.dp
    val GapL = 16.dp
    val GapXl = 24.dp
    val GapXxl = 32.dp

    val CardCorner = 20.dp
    val CardPadding = 18.dp
    val ChipCorner = 999.dp

    /** 最小可点击高度：中老年人手指点击，不能小于 48dp */
    val MinTouchHeight = 56.dp
    val ButtonHeight = 56.dp
    val IconSize = 24.dp
    val BadgeDot = 10.dp
}
