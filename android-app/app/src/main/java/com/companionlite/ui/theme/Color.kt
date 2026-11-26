package com.companionlite.ui.theme

import androidx.compose.ui.graphics.Color

/*
 * 配色说明（给成员 A 自己看的，也方便答辩时解释）：
 * 1. 主色用「暖陶土橙」，不用医疗蓝：这个 App 是陪伴，不是医疗设备。
 * 2. 所有正文文字都在浅奶油色底上，与背景对比度 ≥ 4.5:1，符合 WCAG AA，
 *    对老花眼更友好。
 * 3. 「数据可信度」6 种状态各有固定颜色，全 App 一致，用户看颜色就知道
 *    是"有数据""没数据"还是"设备离线"。
 */

// ---------- 主色 ----------
val WarmPrimary = Color(0xFFB4572C)        // 白字压在上面，对比度约 5.1:1
val WarmPrimaryDark = Color(0xFF8E4220)
val WarmPrimaryLight = Color(0xFFE08A5F)   // 只用于装饰线条，不承载文字
val WarmContainer = Color(0xFFFBE6D9)
val OnWarmContainer = Color(0xFF5A2A14)

// ---------- 背景与表面 ----------
val CreamBackground = Color(0xFFFFF8F3)
val SurfaceWhite = Color(0xFFFFFFFF)
val SurfaceSunken = Color(0xFFF7EFE8)
val DividerSoft = Color(0xFFEFE4DA)

// ---------- 文字 ----------
val InkText = Color(0xFF2B2724)
val InkSoft = Color(0xFF6B615A)
val InkFaint = Color(0xFF8A7F77)

// ---------- 数据可信度 6 态 ----------
val TrustNormal = Color(0xFF2F6E4E)        // 正常记录
val TrustNormalBg = Color(0xFFE3F0E8)
val TrustUser = Color(0xFF2C5F8A)          // 本人反馈
val TrustUserBg = Color(0xFFE2EDF6)
val TrustWait = Color(0xFF8A5A0B)          // 同步延迟 / 待确认
val TrustWaitBg = Color(0xFFFBEFD6)
val TrustMissing = Color(0xFF5B6672)       // 数据缺失 / 数据不足
val TrustMissingBg = Color(0xFFE8EDF2)
val TrustAlert = Color(0xFF9E3623)         // 需要关注（不是"危险"）
val TrustAlertBg = Color(0xFFF7E1DC)
