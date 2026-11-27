# 接口文档 v2.0（已定稿）

> **维护**：成员 C（后端实现）｜**本次重写**：成员 A，2026-11-27，依据 `backend/app` 的实际代码与 `/openapi.json`
> **状态**：v2.0 **已定稿**，以本文件 + 后端代码为唯一事实来源。v1 草案已作废。
> 改动代码前先看第 0 节，它列出了 v1 和实际实现差在哪。

---

## 0. 与 v1 草案相比，改了什么

| 项 | v1 草案（作废） | v2.0 实际实现 |
| --- | --- | --- |
| 路径风格 | `/check-ins`、`/users/me`、`/baseline` | `/checkins`、`/auth/me`、`/baselines/me` |
| 查询本人数据 | `GET /checkins` | `GET /checkins/me`（一律带 `/me`） |
| 关怀事件回馈 | `POST /care-events/{id}/feedback` | `POST /care-events/{event_id}/respond` |
| 授权修改 | `PATCH /family/links/{id}` | `PUT /family/links/{link_id}/permission` |
| 接口数量 | 16 | **43 个操作 / 11 个模块** |
| `activity_type` | `wake/out/home/medicine` | `wake_up/go_out/go_home/medication` |
| `mood` | 未定义 | `happy/calm/tired/low` |
| `trust_state` | 未定义 | 每条记录都返回，取值见第 2 节 |

---

## 1. 通用约定

| 项 | 约定 |
| --- | --- |
| Base URL（本机） | `http://127.0.0.1:8000` |
| Base URL（真机） | `http://<电脑局域网IP>:8000`（手机与电脑同一 WiFi） |
| 前缀 | 所有业务接口都在 `/api/v1` 下 |
| 认证 | `Authorization: Bearer <access_token>` |
| 时间 | 请求与响应统一 **ISO-8601 UTC**（`2026-11-27T00:30:00Z` 或 `+00:00`）；展示时由客户端转本地时间 |
| 字段名 | **snake_case**；Android 侧用 `@SerializedName` 映射成驼峰 |
| 空列表 | 返回 `[]`，不返回 `null` |
| 内容类型 | `application/json; charset=utf-8` |
| 文档 | 启动后 <http://127.0.0.1:8000/docs>（Swagger，可当场调试） |

---

## 2. 枚举总表（全队唯一事实来源）

> 这张表是**唯一标准**。任何模块新增取值，必须先改这里，再改代码。
> 后端用白名单校验，传错值直接 4xx。

| 概念 | 取值 | 说明 | 权威实现 |
| --- | --- | --- | --- |
| `activity_type` | `wake_up` `go_out` `go_home` `meal` `exercise` `rest` `medication` `other` | 活动类型 | 后端 `schemas/activity.py` |
| `status`（签到） | `normal` `good` `uncomfortable` `need_help` | **身体感觉** | 后端 `schemas/checkin.py` |
| `mood`（心情） | `happy` `calm` `tired` `low` | **心情**，不要和 status 混用 | 后端 `schemas/checkin.py` |
| `data_source` | `manual` `device` | 本人填写 / 设备采集 | 后端 `schemas/checkin.py` |
| `sync_status` | `synced` `pending` `failed` | 同步状态 | 后端 `schemas/checkin.py` |
| **`trust_state`** | `normal` `missing_unknown` `device_offline` `sync_delay` `user_feedback` `insufficient` | **数据可信度**，项目核心字段 | 算法 `companion_algo/trust.py`（后端透传，不得自判） |
| `event_type` | `checkin_delay` `activity_drop` `feedback_concern` `user_request` `sos` | 关怀事件类型 | 后端 `schemas/care.py` |
| `event_status` | `pending` `asking` `answered` `family_pending` `closed` | 关怀事件状态机 | 后端 `schemas/care.py` |
| `concern_level` | `low` `medium` `high` | 关注级别，**不是诊断结论** | 后端 `schemas/care.py` |
| `response` / `feedback_type` | `fine` `busy` `unwell` `want_family_contact` `no_answer`（反馈接口另允许 `other`） | 本人对询问的回答 | 后端 `schemas/care.py` |
| `role` | `self`（本人）`family`（家属） | 账号角色 | 后端 `schemas/user.py` |
| 家属授权范围 | `checkins` `activities` `health` `care_events` `feedback` `baseline` | `permission_scope` 数组的合法值 | 后端 `schemas/family.py` |

### `trust_state` 的含义（界面必须能区分）

| 值 | 界面标签 | 含义 | 界面措辞要求 |
| --- | --- | --- | --- |
| `normal` | 正常记录 | 数据完整有效 | —— |
| `user_feedback` | 本人反馈 | 本人主动填写 | —— |
| `sync_delay` | 同步延迟 | 数据还没同步完成 | "稍后再看" |
| `device_offline` | 设备离线 | 已知设备离线 | "设备离线" |
| `missing_unknown` | 数据缺失 | 没收到数据，**原因未知** | 只能写"还没有收到记录" |
| `insufficient` | 数据不足 | 历史样本不足 | "暂不判断" |

> **禁止**：把 `missing_unknown` / `device_offline` / `sync_delay` 显示成"异常""危险""出事了"。
> 这是本项目的产品原则，也是答辩的核心论点。

---

## 3. 认证与权限

1. 除 `POST /auth/register`、`POST /auth/login`、`GET /` 外，**所有接口都要 token**。
2. 密码只存 bcrypt 哈希，任何响应都不返回密码字段。
3. 家属只能访问 `permission_scope` 里授权的数据；**撤销授权后立即失效**，后端返回 403。
4. 本人只能读写自己的数据；`/me` 系列接口自动取当前 token 的用户，不接受客户端传 user_id。
5. **权限判断只在后端做**，Android 端隐藏按钮不算权限控制。

---

## 4. 接口清单（43 个操作）

> 标注：🔓 无需登录　🔒 需要 token　👨‍👩‍👧 家属身份 + 已授权

### 4.1 账号 auth（4）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | 注册（本人 / 家属） | 🔓 |
| POST | `/api/v1/auth/login` | 登录，返回 access_token | 🔓 |
| GET | `/api/v1/auth/me` | 当前账号资料 | 🔒 |
| PUT | `/api/v1/auth/me` | 修改资料（称呼、手机、时区等） | 🔒 |

### 4.2 签到 checkins（3）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/checkins` | 提交签到 | 🔒 |
| GET | `/api/v1/checkins/me` | 我的签到（可带 `from` / `to`） | 🔒 |
| GET | `/api/v1/checkins/me/today` | 我今天的签到 | 🔒 |

### 4.3 活动 activities（4）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/activities` | 新增活动记录 | 🔒 |
| GET | `/api/v1/activities/me` | 我的活动（可带 `from` / `to`） | 🔒 |
| PUT | `/api/v1/activities/{activity_id}` | 修改一条活动 | 🔒 |
| DELETE | `/api/v1/activities/{activity_id}` | 删除一条活动 | 🔒 |

### 4.4 家庭 family（6）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/family/invite-code` | 本人生成 6 位邀请码（60 分钟有效） | 🔒 |
| POST | `/api/v1/family/bind` | 家属用邀请码申请绑定 | 🔒 |
| GET | `/api/v1/family/links` | 家庭关系列表（本人看家属、家属看本人） | 🔒 |
| PUT | `/api/v1/family/links/{link_id}/confirm` | 本人确认绑定 | 🔒 |
| PUT | `/api/v1/family/links/{link_id}/permission` | 本人设置授权范围 / 接收提醒 | 🔒 |
| DELETE | `/api/v1/family/links/{link_id}` | 撤销授权 / 解除绑定 | 🔒 |

### 4.5 关怀事件 care-events（10）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/care-events` | 创建事件（通常由算法或本人触发） | 🔒 |
| GET | `/api/v1/care-events/me` | 我收到的关怀事件 | 🔒 |
| GET | `/api/v1/care-events/family` | 家属可看的、已授权的事件 | 👨‍👩‍👧 |
| GET | `/api/v1/care-events/{event_id}` | 事件详情 | 🔒 |
| POST | `/api/v1/care-events/{event_id}/ask` | 向本人发起询问（pending → asking） | 🔒 |
| POST | `/api/v1/care-events/{event_id}/respond` | **本人回答**（asking → answered） | 🔒 |
| POST | `/api/v1/care-events/{event_id}/notify-family` | 通知家属（→ family_pending） | 🔒 |
| POST | `/api/v1/care-events/{event_id}/mark-contacted` | 家属标记"已联系" | 👨‍👩‍👧 |
| POST | `/api/v1/care-events/{event_id}/close` | 关闭事件（→ closed） | 🔒 |
| POST | `/api/v1/care-events/sos` | 一键求助（`user_request` + 高优先级） | 🔒 |

### 4.6 反馈 feedback（2）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/feedback` | 主动反馈（**"希望家人联系我"就走这里**） | 🔒 |
| GET | `/api/v1/feedback/me` | 我的反馈历史 | 🔒 |

### 4.7 基线 baselines（3）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| GET | `/api/v1/baselines/me` | 我的个人生活基线 | 🔒 |
| POST | `/api/v1/baselines/me/recalculate` | 重算基线（调算法包） | 🔒 |
| POST | `/api/v1/baselines/me/detect-changes` | 跑一次变化识别，可能生成事件 | 🔒 |

### 4.8 看板 dashboard（2）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| GET | `/api/v1/dashboard/self` | 本人首页聚合数据 | 🔒 |
| GET | `/api/v1/dashboard/family/{user_id}` | 家属看已授权用户的聚合数据 | 👨‍👩‍👧 |

### 4.9 设备 devices（4）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/devices` | 绑定设备 | 🔒 |
| GET | `/api/v1/devices/me` | 我的设备列表 | 🔒 |
| PUT | `/api/v1/devices/{device_id}/status` | 更新设备在线状态 | 🔒 |
| DELETE | `/api/v1/devices/{device_id}` | 解绑设备 | 🔒 |

### 4.10 健康数据 health-records（2）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/health-records` | 上报设备数据（步数等） | 🔒 |
| GET | `/api/v1/health-records/me` | 我的设备数据 | 🔒 |

### 4.11 同步日志 sync-logs（2）

| 方法 | 路径 | 说明 | 权限 |
| --- | --- | --- | --- |
| POST | `/api/v1/sync-logs` | 记录一次同步（成功/失败/延迟） | 🔒 |
| GET | `/api/v1/sync-logs/me` | 我的同步记录 | 🔒 |

---

## 5. 关键接口的请求 / 响应示例

### 5.1 注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "laowang",
  "password": "123456",
  "display_name": "王秀兰",
  "phone": "13800000001",
  "role": "self",
  "timezone": "Asia/Shanghai"
}
```

- `username`：3–50 位，**登录用它**，不是手机号
- `role`：`self`（本人）/ `family`（家属）
- 成功：`201`，返回用户资料（不含密码）

### 5.2 登录

```http
POST /api/v1/auth/login

{ "username": "laowang", "password": "123456" }
```

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer", "user": { "id": 1, "username": "laowang", "role": "self" } }
```

### 5.3 提交签到

```http
POST /api/v1/checkins
Authorization: Bearer <token>

{
  "check_in_at": "2026-11-27T00:30:00Z",
  "mood": "happy",
  "status": "good",
  "note": "今天状态不错",
  "data_source": "manual",
  "sync_status": "synced"
}
```

响应 `201`：

```json
{
  "id": 12,
  "user_id": 1,
  "check_in_at": "2026-11-27T00:30:00Z",
  "mood": "happy",
  "status": "good",
  "note": "今天状态不错",
  "data_source": "manual",
  "sync_status": "synced",
  "is_confirmed": true,
  "trust_state": "user_feedback",
  "created_at": "2026-11-27T00:30:05Z"
}
```

> `trust_state` 是**现算的**，不是数据库列；由后端调用 `companion_algo.trust.record_trust_state` 得到。

### 5.4 新增活动

```http
POST /api/v1/activities
Authorization: Bearer <token>

{
  "activity_type": "go_out",
  "recorded_at": "2026-11-27T01:10:00Z",
  "note": "去菜市场",
  "data_source": "manual",
  "sync_status": "synced"
}
```

响应同上结构，多了 `trust_state`。

### 5.5 本人回答主动询问

```http
POST /api/v1/care-events/9001/respond
Authorization: Bearer <token>

{ "response": "want_family_contact" }
```

- `response` 取值：`fine` / `busy` / `unwell` / `want_family_contact` / `no_answer`
- 只有 `want_family_contact`、`unwell` 在已授权的前提下才会通知家属
- 事件状态：`asking` → `answered`

### 5.6 "希望家人联系我"（签到页的开关）

签到接口**没有** `want_family_call` 字段，走反馈接口：

```http
POST /api/v1/feedback

{ "feedback_type": "want_family_contact", "content": "今天有点不舒服，想让人来看看" }
```

### 5.7 个人基线

```http
GET /api/v1/baselines/me
Authorization: Bearer <token>
```

```json
{
  "user_id": 1,
  "window_days": 14,
  "checkin_time_median": "07:52:00",
  "checkin_time_mean": "07:58:00",
  "checkin_time_stddev": 12.5,
  "checkin_iqr_min": "07:36:00",
  "checkin_iqr_max": "08:16:00",
  "avg_daily_activities": 4.6,
  "avg_weekly_activities": 32.0,
  "avg_daily_steps": null,
  "valid_days": 11,
  "data_sufficient": true,
  "calculated_at": "2026-11-27T02:00:00Z"
}
```

> `data_sufficient = false` 时，客户端**必须**显示"数据不足，暂不判断"，不能展示任何结论。

---

## 6. 错误码

| HTTP | detail 示例 | 含义 | 客户端怎么做 |
| --- | --- | --- | --- |
| 400 | `mood 取值不合法` | 参数白名单校验失败 | 修字段值，不要重试 |
| 401 | `Not authenticated` / token 过期 | 未登录 | 跳登录页，清 token |
| 403 | `无权访问该用户的数据` | 家属未授权 / 授权已撤销 | 提示"没有权限"，不要重试 |
| 404 | `Not Found` | 路径写错或资源不存在 | **先核查路径**，v1 的旧路径会走到这里 |
| 409 | 重复签到 | 冲突 | 提示"今天已经签到过了" |
| 422 | Pydantic 校验失败（带字段名） | 缺字段 / 类型错 | 看返回的 `loc` 定位字段 |

---

## 7. 给 Android 端的注意事项

1. **路径一律带 `/me`**（除 auth 和 family），不要写 `/checkins` 取列表。
2. `activity_type` 只能传 8 个英文值，传中文会 400。
3. `mood` 和 `status` 是两套词，别混。
4. 列表接口每条记录都带 `trust_state`，直接映射成界面的可信度标签，**不要自己判断**。
5. 403 和 404 要区分：403 是权限问题（提示用户），404 是路径问题（开发 bug）。
6. 所有时间都是 UTC 字符串，展示前转本地时区。

---

## 8. 变更记录

| 版本 | 日期 | 变更 | 作者 |
| --- | --- | --- | --- |
| v1.0 | 2026-11-26 | 初始草案（16 个接口，未定稿） | A |
| v2.0 | 2026-11-27 | 按后端实际实现重写：43 个操作、路径带 `/me`、补 `trust_state` 与全部枚举、补错误码 | A（依据 C 的实现） |
