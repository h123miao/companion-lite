# 接口文档（草案 v0.1）

> 负责人：成员 C ｜ 状态：**草案，由 C 定稿后其他人按此开发**
>
> 本文件由 A 起草的"公共字段约定"部分来源于《分工.md》第五节，C 确认/修订后把状态改成"已定稿"。
> 任何人不得在代码里使用本文件以外的字段名。

---

## 1. 通用约定

| 项目 | 约定 |
| --- | --- |
| Base URL（本地） | `http://127.0.0.1:8000` |
| Base URL（手机访问） | `http://<电脑局域网IP>:8000` |
| 前缀 | `/api/v1` |
| 认证 | `Authorization: Bearer <token>` |
| 时间格式 | ISO-8601 UTC，例：`2026-11-26T00:30:00Z`（数据库存 UTC，展示转本地时间） |
| 字符编码 | UTF-8，JSON 字段名一律 **snake_case** |
| 分页 | `?page=1&page_size=20`，返回 `{ "items": [], "total": 0 }` |

统一响应包装（C 决定是否采用）：

```json
{
  "code": 0,
  "message": "ok",
  "data": { }
}
```

错误码：

| code | HTTP | 含义 |
| --- | --- | --- |
| 0 | 200 | 成功 |
| 1001 | 400 | 参数错误 |
| 1002 | 401 | 未登录或 token 失效 |
| 1003 | 403 | 无权限（典型：家属未获授权却查询本人数据） |
| 1004 | 404 | 资源不存在 |
| 1005 | 409 | 冲突（典型：重复签到） |

---

## 2. 公共字段约定（A 的界面依赖这些名字）

| 含义 | 字段名 | 类型 | 说明 |
| --- | --- | --- | --- |
| 用户编号 | `user_id` | int | |
| 签到时间 | `check_in_at` | string(ISO8601) | |
| 活动类型 | `activity_type` | enum | `wake/out/home/meal/exercise/rest/medicine/other` |
| 活动时间 | `recorded_at` | string(ISO8601) | |
| 数据来源 | `data_source` | string | `phone` / `watch` / `manual` |
| 同步状态 | `sync_status` | enum | `synced/pending/failed` |
| 反馈内容 | `feedback_type` | enum | `i_am_fine/busy/unwell/want_call/no_answer` |
| 关怀事件状态 | `event_status` | enum | `pending/awaiting_family/handled/closed` |
| **数据可信度** | `trust_state` | enum | 见下，**界面必须能拿到这个字段** |

### `trust_state` 取值（A 强烈要求保留，界面的核心表达靠它）

| 值 | 界面标签 | 含义 |
| --- | --- | --- |
| `normal` | 正常记录 | 数据完整有效 |
| `missing` | 数据缺失 | 没收到预期数据，原因未知 |
| `offline` | 设备离线 | 已知设备离线 |
| `delayed` | 同步延迟 | 还没同步完成 |
| `user_feedback` | 本人反馈 | 本人主动填写 |
| `insufficient` | 数据不足 | 历史样本不足，无法判断 |

签到示例：

```json
{
  "user_id": 1001,
  "check_in_at": "2026-11-26T00:30:00Z",
  "mood": "good",
  "status": "normal",
  "note": "今天状态不错",
  "want_family_call": false,
  "data_source": "manual",
  "sync_status": "synced",
  "trust_state": "user_feedback"
}
```

---

## 3. 接口清单（待 C 补全请求/响应细节）

### 3.1 用户与家庭

| 方法 | 路径 | 说明 | 谁用 |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | 注册（角色：`elder` / `family`） | A/B |
| POST | `/api/v1/auth/login` | 登录，返回 token 与角色 | A/B |
| GET | `/api/v1/users/me` | 当前用户资料 | A/B |
| POST | `/api/v1/family/invite-code` | 生成本人的家庭邀请码 | A/B |
| POST | `/api/v1/family/bind` | 家属用邀请码申请绑定 | B |
| POST | `/api/v1/family/bind/{link_id}/confirm` | 本人确认绑定 | A/B |
| GET | `/api/v1/family/members` | 本人家属列表与授权状态 | A/B |
| PATCH | `/api/v1/family/links/{link_id}` | 修改授权范围 / 撤销授权 | A/B |

### 3.2 生活记录

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/v1/check-ins` | 提交签到 |
| GET | `/api/v1/check-ins?from=&to=` | 查询签到（含 `trust_state`） |
| POST | `/api/v1/activities` | 新增活动记录 |
| GET | `/api/v1/activities?from=&to=` | 查询活动 |
| GET | `/api/v1/timeline?days=14` | 时间线（签到 + 活动合并，供 P6 用） |

### 3.3 分析与关怀

| 方法 | 路径 | 说明 | 谁算 |
| --- | --- | --- | --- |
| GET | `/api/v1/baseline` | 个人生活基线（P7 用） | D 算，C 出 |
| GET | `/api/v1/care-events?status=` | 关怀事件列表 | C |
| POST | `/api/v1/care-events/{id}/feedback` | 本人回答主动询问 | A/B 提交 |
| PATCH | `/api/v1/care-events/{id}/status` | 家属标记已联系 / 已处理 | B |

---

## 4. 权限规则（C 必须实现，A 只负责界面）

1. 家属查询本人数据时，后端必须校验 `family_links` 的授权状态与授权范围，**不能只靠 Android 端隐藏按钮**。
2. 撤销授权后立即生效：后续请求返回 `1003`。
3. 本人只能读写自己的数据；家属只能读被授权的数据，不能写本人的生活记录。
4. 密码只存哈希（bcrypt / argon2），接口永远不返回密码字段。

---

## 5. 给 A 的最小契约（只要满足这几条，界面就能全部接上）

1. 列表里的每一条记录都带 `trust_state`。
2. 时间一律 ISO-8601 UTC 字符串，A 负责转本地时间显示。
3. 空列表返回 `[]` 而不是 `null`。
4. 出错时返回统一错误码，A 把它变成页面上的红字提示。
