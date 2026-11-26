# Android 环境搭建与常见报错

## 1. 装什么

| 软件 | 版本 | 说明 |
| --- | --- | --- |
| Android Studio | 2024.2.1（Ladybug）或更新 | 安装时勾选 Android SDK、SDK Platform 35 |
| JDK | 17（Android Studio 自带 jbr 即可） | 不要装 JDK 21 以上，AGP 8.7 只认 17 |
| Gradle | 8.9（wrapper 自动下载，不用手动装） | 项目里已经配好 |

项目配置：`compileSdk 35`、`minSdk 26`、`targetSdk 35`、Kotlin 2.0.21、AGP 8.7.3。

> 关于下载速度：`gradle-wrapper.properties` 里的 Gradle 发行包地址已经指向国内镜像
> `https://mirrors.cloud.tencent.com/gradle/gradle-8.9-bin.zip`，`settings.gradle.kts` 里也配了阿里云 Maven 镜像。
> 如果哪天镜像挂了，把它改回官方地址 `https://services.gradle.org/distributions/gradle-8.9-bin.zip` 即可。

---

## 2. 第一次打开

1. `File → Open`，选 **`android-app`** 目录（不是仓库根目录，根目录没有 Gradle 工程）。
2. 右下角出现 "Gradle Sync"，等它跑完（第一次要下依赖，5～10 分钟正常）。
3. 第一次可能需要设置 SDK 路径：`File → Project Structure → SDK Location`。
4. 选模拟器（Device Manager 里建一个 Pixel 6 / API 35）或插上手机（开启开发者模式 + USB 调试）。
5. 点绿色 ▶ 运行。

---

## 3. 常见报错

### 3.1 `Could not find com.android.tools.build:gradle:8.7.3`

国内网络问题。项目 `settings.gradle.kts` 里已经配了阿里云镜像，如果还失败：

- 检查是否在公司/学校网络下被代理拦截；
- 换成手机热点试一次；
- 真不行把 `settings.gradle.kts` 里的阿里云两行注释掉，只用 `google()` + `mavenCentral()`，然后 `File → Invalidate Caches / Restart`。

### 3.2 `SDK location not found`

在 `android-app/local.properties` 里加（路径换成你自己的）：

```properties
sdk.dir=C\:\\Users\\你的用户名\\AppData\\Local\\Android\\Sdk
```

这个文件**不要提交**，`.gitignore` 已经屏蔽。

### 3.3 `Unsupported class file major version 65`

JDK 版本太高（65 = Java 21）。`File → Settings → Build, Execution, Deployment → Build Tools → Gradle → Gradle JDK` 选 17。

### 3.4 `Unresolved reference: xxx`（一堆红色）

九成是 Gradle 没同步成功。按顺序试：

1. `File → Sync Project with Gradle Files`
2. `Build → Clean Project`，再 `Build → Rebuild Project`
3. `File → Invalidate Caches / Restart`

### 3.5 手机连不上 / 一直 `Waiting for device`

- 数据线要能传数据（有些线只能充电）；
- 手机端：开发者选项 → USB 调试 打开；插上后手机上点"允许调试"；
- 小米/华为还要额外打开"USB 安装"。

### 3.6 运行报 `ClassNotFoundException` / 闪退

先看 Logcat 的红色 `FATAL EXCEPTION` 那一段，把前 20 行贴到群里。
不要只说"闪退了"，AI 也没法猜。

---

## 4. 命令行编译（不打开 Android Studio 也能验证）

```bash
cd android-app
./gradlew assembleDebug          # macOS / Linux
gradlew.bat assembleDebug        # Windows
```

成功后会生成 `app/build/outputs/apk/debug/app-debug.apk`。
**只打开 Android Studio 点了运行、看到界面，才算真正跑通**，编译通过不代表界面没错。

---

## 5. 提交前自查

- [ ] `git status` 里没有 `local.properties`、`.idea/`、`build/`
- [ ] 只改了自己负责的目录
- [ ] 打开 App 点一遍自己改的页面
- [ ] 没有新增 `println` / `Toast` 调试残留
