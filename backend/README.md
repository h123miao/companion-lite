# backend / —— FastAPI 后端

> 主要负责人：**成员 C**（后端全部模块）

## 在 `backend/` 目录下运行

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload      # Windows / macOS / Linux 通用
```

启动后访问：

- Swagger 文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/>

运行测试：

```bash
pytest -q
```

## 目录结构

```text
app/
├── main.py               FastAPI 入口（lifespan 建表 + 挂载路由）
├── config.py             配置（环境变量覆盖）
├── database.py           引擎 / Session / Base
├── core/                 安全（bcrypt + JWT）、时间统一处理
├── models/               SQLAlchemy ORM 模型（10 张表）
├── schemas/              Pydantic 请求 / 响应模型
├── algorithm_adapter/    算法接入层（成员 D 的替换点）
├── services/             业务逻辑（基线 / 邀请码 / 授权）
└── api/v1/               路由（15 个模块，挂在 /api/v1 下）
tests/                    8 个测试文件 + conftest（内存 SQLite）
```

## 与算法模块的边界

后端只负责组装输入、调用算法、保存输出，**不实现算法逻辑**。
成员 D 提供 `algorithm/` 目录的正式实现后，替换 `app/algorithm_adapter/baseline.py`
中的调用即可，输入输出格式保持不变。

## 几个约定

- **时间**：数据库一律存 UTC（naive datetime，语义为 UTC），展示时按 `user.timezone` 转换。
- **数据可信度**：少于 7 个有效本地日期时 `data_sufficient=False`，此时不产出任何变化结论。
- **家属授权**：所有家属访问本人数据都经过 `services/permission.py` 校验，撤销授权后立即拒绝。
- **一键呼救**：由本人主动触发，系统不自动拨打 120。

## 不要提交

`*.db`、`backend/data/`、`__pycache__/`、`.venv/` —— `.gitignore` 已屏蔽。

完整源码与讲解见 [../docs/backend-source-code.md](../docs/backend-source-code.md)。
