# 项目文档索引

| 文档 | 负责人 | 说明 |
| --- | --- | --- |
| [android-ui-design.md](android-ui-design.md) | A | **本人端 UI 设计**：页面清单、跳转图、首页布局、视觉规范、数据需求、验收清单 |
| [api.md](api.md) | C（A 于 2026-11-27 按实际代码重写） | **接口文档 v2.0 已定稿**：43 个操作、枚举总表、错误码。所有人按这一份开发 |
| [database.md](database.md) | C | 数据表与 ER 关系 |
| [architecture.md](architecture.md) | C | 后端分层与部署方式 |
| [collaboration.md](collaboration.md) | A（执行） | 分支、提交、每日汇报、冲突处理 |
| [android-dev-setup.md](android-dev-setup.md) | A | Android 环境搭建与常见报错 |

规则：

1. **谁负责的文档谁改**，其他人只读，有意见在群里说。
2. 接口字段一旦确定，先写进 `api.md` 再写代码，不允许"代码里叫这个名字、文档里叫那个名字"。
3. 文档和代码在同一个提交里改，不允许"先改代码，文档以后补"。
