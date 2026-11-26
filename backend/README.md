# backend / —— 成员 C 的后端目录

> 负责人：**成员 C** ｜ 其他人不要改这个目录

## 这里放什么

```text
backend/
├── requirements.txt          # 依赖清单（C 维护）
├── .env.example              # 环境变量示例（不要把真实密钥提交）
└── app/
    ├── main.py               # FastAPI 入口
    ├── core/                 # 配置、安全（密码哈希、JWT）
    ├── models/               # SQLAlchemy 模型
    ├── schemas/              # Pydantic 模型
    ├── api/v1/               # 路由：auth / users / family / checkins / activities / care_events
    ├── crud/                 # 数据库操作
    └── services/             # 业务逻辑（调用 algorithm/）
```

## 怎么跑起来

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate              # Windows
# source .venv/bin/activate         # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger 文档：<http://127.0.0.1:8000/docs>
- 手机访问：`http://<电脑局域网IP>:8000`（手机和电脑连同一个 WiFi）

## 必须遵守

1. 接口路径、字段名以 `docs/api.md` 为准，改了先改文档。
2. 列表接口每一条记录都要带 `trust_state`（Android 界面靠它区分"没数据"和"没活动"）。
3. 时间统一存 UTC。
4. 密码只存哈希。
5. 家属查询必须校验 `family_links` 的授权，撤销后立即生效。
6. 不提交 `*.db`、`.env`、`.venv/`。

## 当前状态

⏳ 等待 C 提交第一个可运行版本（用户注册 + 签到接口）。
Android 端先用 `android-app/.../data/mock/MockRepository.kt` 里的模拟数据跑界面。
