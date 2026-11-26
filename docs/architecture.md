# 技术架构（待成员 C 补充后端部分）

> 负责人：成员 C ｜ 状态：**骨架已定，细节待补**

## 已确定的技术栈（不允许擅自更换）

| 层 | 技术 |
| --- | --- |
| Android | Kotlin 2.0.21、Jetpack Compose、Navigation Compose、Material 3、MVVM |
| Android 网络 | Retrofit + OkHttp（成员 B 引入） |
| Android 本地 | Room（成员 B 引入） |
| 后端 | Python 3.11/3.12、FastAPI、SQLAlchemy 2.x、Pydantic v2 |
| 数据库 | SQLite（初期），后续可迁 MySQL |
| 算法 | Python、NumPy、Pandas、规则引擎、pytest |
| 构建 | Gradle 8.9 + AGP 8.7.3，JDK 17 |

## 三层结构

```text
Android (Kotlin/Compose)
    │  Retrofit + JSON
    ▼
FastAPI（/api/v1）
    │  SQLAlchemy ORM
    ▼
SQLite
    ▲
    │  函数调用（不是 HTTP）
algorithm/（成员 D 的基线与可信度算法）
```

## 几条架构纪律

1. **算法不放在后端进程里手写一遍**：`algorithm/` 是一个独立的 Python 包，后端 `import` 它，D 可以单独 `pytest` 测试。
2. **Android 不实现业务规则**：界面上显示"数据不足/缺失"完全来自后端字段，客户端不自己判断。
3. **所有权限判断在后端**：Android 只负责隐藏不该看到的入口，不作为安全边界。
4. **模拟数据与真实数据在同一套接口后面**：D 的 `test-data/` 通过脚本灌进数据库，接口不用改。

## 待补充

- 后端目录结构（C）
- 启动方式与依赖清单（C）
- 部署方式：本地 `uvicorn` / 局域网手机访问 / 是否需要云服务器（C）
