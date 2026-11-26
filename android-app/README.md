# android-app / —— Android 客户端

> 主要负责人：**成员 A**（`ui/`）、**成员 B**（`data/`）

## 用 Android Studio 打开**这个目录**（不是仓库根目录）

1. `File → Open` → 选择 `android-app`
2. 等 Gradle Sync 完成（第一次 5～10 分钟）
3. 选择模拟器或真机 → ▶ 运行

命令行编译：

```bash
cd android-app
gradlew.bat assembleDebug        # Windows
./gradlew assembleDebug          # macOS / Linux
```

## 目录分工（重要）

```text
app/src/main/java/com/companionlite/
├── MainActivity.kt
├── ui/        ← 成员 A：页面、组件、主题、导航、页面状态
└── data/      ← 成员 B：网络、Repository、Room、数据模型、Session
```

- A 只改 `ui/`，B 只改 `data/`。
- `app/build.gradle.kts` 两个人都可能改（加依赖），**改之前先在群里说一句**。
- UI 层现在用的模拟数据在 `data/mock/MockRepository.kt`，B 接入后端后替换这一层，页面代码不用动。

## 技术栈

| 项目 | 版本 |
| --- | --- |
| Kotlin | 2.0.21 |
| AGP | 8.7.3 |
| Gradle | 8.9（wrapper 自动下载） |
| Compose BOM | 2024.10.01 |
| Navigation Compose | 2.8.4 |
| compileSdk / targetSdk | 35 |
| minSdk | 26（为了直接用 java.time，且覆盖面足够） |
| JDK | 17 |

所有依赖版本集中在 `gradle/libs.versions.toml`，升级只改那一个文件。

## 页面与代码的对应

| 页面 | 文件 |
| --- | --- |
| 登录 | `ui/screens/auth/LoginScreen.kt` |
| 注册 | `ui/screens/auth/RegisterScreen.kt` |
| 首页 | `ui/screens/home/HomeScreen.kt` |
| 主动询问弹窗 | `ui/screens/home/CareAskDialog.kt` |
| 每日签到 | `ui/screens/checkin/CheckInScreen.kt` |
| 活动记录 | `ui/screens/activity/ActivityRecordScreen.kt` |
| 历史时间线 | `ui/screens/timeline/TimelineScreen.kt` |
| 生活规律统计 | `ui/screens/stats/StatsScreen.kt` |
| 我的 | `ui/screens/profile/ProfileScreen.kt` |

页面设计说明见 [../docs/android-ui-design.md](../docs/android-ui-design.md)。

## 不要提交

`local.properties`、`.idea/`、`build/`、`*.apk`、`*.jks` —— `.gitignore` 已经屏蔽，别用 `git add -f` 强行加。
