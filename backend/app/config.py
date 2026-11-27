"""项目配置。所有敏感值通过环境变量覆盖，开发时有默认值。"""

import os
from pathlib import Path

# 项目根目录：backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite 数据库文件路径
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'companionlite.db'}")

# JWT 密钥（开发用默认值，生产必须改）
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 小时
