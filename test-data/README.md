# test-data / —— 模拟测试数据

> 负责人：**成员 D** ｜ 其他人只读

## 要求

- 10 个虚拟用户，每人 30 天记录。
- 覆盖：正常作息 / 晚睡晚起 / 偶尔漏签到 / 连续漏签到 / 设备离线 / 网络中断 / 同步延迟 / 用户主动反馈 / 历史数据不足 / 未授权家属访问。

## 建议结构

```text
test-data/
├── users.json               # 10 个虚拟用户
├── checkins_30d.json        # 签到记录（含缺失、离线、延迟）
├── activities_30d.json      # 活动记录
├── care_events_expected.json# 期望生成的关怀事件（用于算准确率）
└── README.md
```

**所有文件必须能一眼看出是模拟数据**：文件名带 `_30d`、内容里带 `"is_synthetic": true`。

## 怎么用

后端提供导入脚本（C 写）把 JSON 灌进 SQLite，Android 端不需要改任何代码。
