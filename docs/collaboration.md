# 协作规则

四个人、初学者团队。**这套规则的唯一目的：让四份代码最后能拼起来。**

---

## 1. 目录归属（最重要的一条）

```text
android-app/  ui/      → A    页面、组件、主题、导航、页面状态
android-app/  data/    → B    网络、Repository、Room、数据模型、Session
backend/               → C    FastAPI、SQLAlchemy、权限
algorithm/             → D    基线、可信度、变化识别、pytest
test-data/             → D    10 个虚拟用户 × 30 天模拟数据
docs/api.md、database.md → C  接口与表结构
docs/android-*.md      → A   UI 设计与环境说明
```

**只改自己目录里的文件。** 需要别人改，就在群里说清楚「哪个文件、哪一行、为什么」。

例外：`android-app/app/build.gradle.kts` 是 A 和 B 都要动的文件。
约定：**每次改之前先在群里说一句**，改完在 PR 描述里写"我加了什么依赖"。

---

## 2. 分支

| 成员 | 分支 | 合并目标 |
| --- | --- | --- |
| A | `feature/android-ui` | `main` |
| B | `feature/android-api` | `main` |
| C | `feature/backend` | `main` |
| D | `feature/algorithm` | `main` |

- `main` 任何时候都必须能跑（Android 能编译、后端能启动）。
- 不允许直接往 `main` 提交（第一次建仓库时除外）。
- 一个功能一个分支也行（`feature/home-checkin`），但分支名要能看出是谁的。

---

## 3. 每天的最小动作

开工前：

```bash
git switch feature/你的分支
git pull                      # 拉最新
git merge main                # 把 main 合进来，冲突现在就解决
```

收工前：

```bash
git status                    # 确认没有把 build/、local.properties 加进来
git add <只加自己目录>
git commit -m "A: 首页与签到页布局完成"
git push
```

然后在 GitHub 上开 PR，写三句话：**做了什么 / 怎么验证 / 有什么没做**。

---

## 4. 提交信息格式

```text
A: 完成首页与签到页布局
B: 接入签到提交接口
C: 增加家庭邀请码接口
D: 实现签到时间基线算法
```

开头那个字母让所有人一眼知道是谁的提交。

---

## 5. 接口变更流程（最容易出事的地方）

1. C 在 `docs/api.md` 里加/改字段 → 提交。
2. 在群里 @A @B @D：「`daily_checkins` 新增了 `trust_state` 字段，取值见文档」。
3. A/B 按新文档改代码。
4. **不允许**先改代码再改文档，也不允许自己发明字段名。

已经确认的字段，任何人不能私自改名。真要改名，C 改文档 → 全员确认 → 一起改。

---

## 6. 冲突怎么处理

看到 `CONFLICT (content)` 不要慌，也不要直接 `git checkout --theirs`：

```bash
git status                 # 看哪几个文件冲突
# 打开文件，找 <<<<<<< 、======= 、>>>>>>> 三段，人工合成最终版本，删掉这些标记
git add 你改好的文件
git commit
```

**改不了就在群里说，别硬提交。** 两个人同时改同一个文件时，后提交的人负责解决冲突。

永远不要 `git push --force`。

---

## 7. 每天的进度汇报

在群里一条消息，三句话：

1. 今天完成了什么（对应哪个页面/接口/算法）
2. 现在卡在哪（报错原文贴出来）
3. 明天做什么

---

## 8. 代码底线（四个人一起守）

1. 没跑过的代码，不说"已完成"。
2. 模拟数据必须在界面上标「演示数据」。
3. 数据缺失不能写进"异常/危险"分支。
4. 密码不明文存，家属权限以后端校验为准。
5. AI 生成的代码，自己先跑通再提交；看不懂的地方问，不要复制粘贴了事。
