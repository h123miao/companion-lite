# 数据库设计（待成员 C 完成）

> 负责人：成员 C ｜ 状态：**空模板，等 C 输出 ER 图与字段表**

## 需要设计的表

1. `users` —— 用户（本人 / 家属），密码哈希
2. `family_links` —— 家庭关系与授权范围
3. `daily_checkins` —— 每日签到
4. `activity_records` —— 活动记录
5. `device_bindings` —— 设备绑定
6. `health_records` —— 穿戴设备数据
7. `data_sync_logs` —— 数据同步日志
8. `baseline_profiles` —— 个人生活基线
9. `care_events` —— 关怀事件
10. `user_feedback` —— 用户反馈

## 每张表必须写清楚

字段名、类型、主键、外键、是否可空、默认值、索引、字段含义。

## 硬性要求

1. 所有时间字段存 UTC（`TIMESTAMP WITH TIME ZONE` 或统一存 UTC 的 `DATETIME`）。
2. `family_links` 必须有 `status`（待确认 / 已绑定 / 已撤销）和授权范围字段。
3. 密码列只存哈希，列名 `password_hash`。
4. `care_events` 必须能存：触发规则、使用的数据、生成原因、当前状态、处理人、处理时间。
5. `daily_checkins` / `activity_records` 需要能表达 `trust_state`（或通过 `data_sync_logs` 推导出来）。

## A 的界面对数据库的依赖

- 首页要一次性拿到：今天的签到、基线、最近 3 条活动、待确认的关怀事件。
- 时间线要按天分组返回近 14 天的签到 + 活动。
- 统计页要拿到基线数值和近 7 天活动数。

（这部分可以靠后端聚合，不要求数据库结构一一对应。）
