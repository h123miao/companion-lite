# 伴行·时序 Companion Lite

> 基于个人生活基线与可信数据分析的主动关怀系统
> 第二十届全国大学生软件创新大赛参赛项目

**仓库地址：<https://github.com/h123miao/companion-lite>**

---

## 0. 一句话说明

本项目是 Android（Kotlin + Jetpack Compose）+ Python 后端（FastAPI + SQLite）+ 算法（Python 统计与规则）三部分组成。
四个人各自只改自己负责的那个目录，通过 `git` 把代码推到本仓库，谁的目录谁负责。

| 成员 | 负责内容 | 只允许改动的目录 | 分支名 |
| --- | --- | --- | --- |
| **A** | Android 页面与 UI | `android-app/` 里的 `ui/` | `feature/android-ui` |
| **B** | Android 网络请求、数据交互、家属端 | `android-app/` 里的 `data/`、`repository/` | `feature/android-api` |
| **C** | Python 后端、数据库、权限、API 文档 | `backend/`、`docs/api.md`、`docs/database.md` | `feature/backend` |
| **D** | 个人基线、数据可信度、变化识别、测试 | `algorithm/`、`test-data/` | `feature/algorithm` |

> **铁律：谁都不许改别人的目录，谁也不许改公共字段名。**
> 需要改别人目录里的东西，先在群里说，由对方改。

---

## 1. 给另外三位同学的 AI 的开场提示词

把下面这段整段复制给 Cursor / ChatGPT / Claude，再补一句"我现在做第几步"：

```text
你在协助我们 4 人初学者团队开发「伴行·时序 Companion Lite」参赛项目。
GitHub 仓库：https://github.com/h123miao/companion-lite
我的身份：成员 X（A=Android UI，B=Android 数据交互，C=后端，D=算法测试）。

必须遵守：
1. 先 git clone 仓库，读 README.md、docs/api.md、docs/collaboration.md，再动手。
2. 只修改我负责的目录，绝对不要碰别人的目录（android-app/ui、android-app/data、backend、algorithm 已划好边界）。
3. 不要擅自新增或重命名公共字段。公共字段见 docs/api.md 的"公共字段约定"一节。
4. 不要编造 API 路径、SDK、第三方接口。接口以 docs/api.md 为准；文档里没有的，先问我。
5. 我刚学编程：每次只做一个功能，告诉我改了哪些文件、怎么运行、怎么验证。
6. 不要把没有实际运行过的代码说成"已完成"。
7. 模拟数据必须在界面上写清"演示数据"，不许伪装成真实设备采集。
```

---

## 2. 第一步：把仓库拉到本地（四个人都一样）

```bash
# 1) 克隆
git clone https://github.com/h123miao/companion-lite.git
cd companion-lite

# 2) 看一下目录（先别急着写代码）
dir            # Windows
ls -R          # macOS / Linux

# 3) 建立自己的分支（分支名见上面表格）
git switch -c feature/android-ui      # A
git switch -c feature/android-api     # B
git switch -c feature/backend         # C
git switch -c feature/algorithm       # D
```

> 第一次 push 可能要登录 GitHub。用 GitHub 账号 + Personal Access Token 当密码；
> 或者在 Android Studio / VS Code 里点 "Sign in with GitHub"。

---

## 3. 第二步：让代码能在你电脑上跑起来

### A、B —— Android 端

1. 安装 **Android Studio**（官方下载即可，装的时候把 Android SDK 一起装上，选 API 35）。
2. `File → Open`，选择仓库里的 **`android-app`** 文件夹（注意：选 `android-app`，不是仓库根目录）。
3. 等右下角 Gradle 同步完成（第一次要下载依赖，可能 5～10 分钟，正常）。
4. 顶部选择一台模拟器或插上手机 → 点绿色 ▶ 运行。

> 如果 Gradle 同步失败，先看 [docs/android-dev-setup.md](docs/android-dev-setup.md) 的"常见错误"。
> **不要**提交 `local.properties`、`.idea/`、`build/` 这些本地文件，`.gitignore` 已经屏蔽，别用 `git add -f` 强行加。

### C —— 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows；macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开 <http://127.0.0.1:8000/docs> 能看到 Swagger 接口文档就算跑通。

被 Android 手机访问时：手机和电脑连同一个 WiFi，把后端地址换成 `http://电脑局域网IP:8000`。

### D —— 算法

```bash
cd algorithm
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

---

## 4. 第三步：把代码推上来（每个人每天都要做）

```bash
# 1) 先看一眼自己改了什么
git status

# 2) 只加自己负责的目录（不要 git add . ，很容易把别人的东西、本地配置一起提交）
git add android-app/app/src/main/java/com/companionlite/ui     # A
git add android-app/app/src/main/java/com/companionlite/data   # B
git add backend docs/api.md docs/database.md                   # C
git add algorithm test-data                                    # D

# 3) 写清楚这次做了什么
git commit -m "A: 完成首页与签到页布局"

# 4) 推到自己分支
git push -u origin feature/android-ui
```

推上去以后，在 GitHub 网页上开一个 **Pull Request**（`feature/xxx` → `main`），
标题写 `A: 首页与签到页`，等 A 看一眼合并。

> 合并前请先 `git switch main && git pull` 再切回自己分支 `git merge main`，
> 这样冲突都在你自己的分支里解决，不会污染 `main`。

### 千万别做的事

- ❌ `git push --force`（会抹掉别人的提交）
- ❌ 直接在 `main` 上改代码、提交
- ❌ 提交 `local.properties`、`.idea/`、`*.db`、`*.jks`、`*.apk`
- ❌ 把别人的目录一起 `git add .` 提交

---

## 5. 公共约定（四个人都必须遵守）

### 5.1 技术栈（已定，不允许擅自更换）

- Android：Kotlin + Jetpack Compose + Navigation Compose + Material 3 + MVVM
- 网络：Retrofit（B 负责）
- 本地缓存：Room（B 负责）
- 后端：Python 3.11/3.12 + FastAPI + SQLAlchemy + Pydantic + SQLite
- 算法：Python + NumPy + Pandas + 规则引擎
- 数据库时间统一存 **UTC**，界面显示时转本地时间

### 5.2 公共字段名（先按这个写，C 负责最终定稿并写进 `docs/api.md`）

| 含义 | 字段名 |
| --- | --- |
| 用户编号 | `user_id` |
| 签到时间 | `check_in_at` |
| 活动类型 | `activity_type` |
| 活动时间 | `recorded_at` |
| 数据来源 | `data_source` |
| 同步状态 | `sync_status` |
| 反馈内容 | `feedback_type` |
| 关怀事件状态 | `event_status` |

### 5.3 数据可信度状态（UI 必须能区分这 6 种，不许把"没数据"说成"有危险"）

`正常记录` / `数据缺失` / `设备离线` / `同步延迟` / `本人反馈` / `数据不足`

---

## 6. 目录说明

```text
companion-lite/
├── android-app/          # A + B：Android 客户端（用 Android Studio 打开这个目录）
│   └── app/src/main/java/com/companionlite/
│       ├── ui/           # ← A 负责：页面、组件、主题、导航
│       └── data/         # ← B 负责：网络、Repository、Room、数据模型
├── backend/              # ← C 负责：FastAPI + SQLAlchemy + SQLite
├── algorithm/            # ← D 负责：个人基线、数据可信度、变化识别、pytest
├── test-data/            # ← D 负责：10 个虚拟用户的 30 天模拟数据
├── docs/                 # 公共文档（api.md / database.md 由 C 维护）
└── demo/                 # 演示视频、答辩材料
```

详细说明见：

- [docs/android-ui-design.md](docs/android-ui-design.md) —— A 的页面设计（页面清单、跳转图、首页布局、设计规范、数据需求）
- [docs/collaboration.md](docs/collaboration.md) —— 协作规则、分支、每日汇报
- [docs/android-dev-setup.md](docs/android-dev-setup.md) —— 环境搭建与常见报错
- [docs/api.md](docs/api.md) —— 接口文档（C 维护，其他人只读）

---

## 7. 每天结束前的三句话

在群里各发一条：

1. 今天完成了什么？
2. 现在卡在哪里？
3. 明天做什么？

---

**让技术不只是监测一个人的数据，而是帮助家人更及时、更准确、更有温度地关心彼此。**
