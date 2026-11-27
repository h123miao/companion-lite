"""FastAPI 应用入口。

启动命令：uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.database import Base, engine

# 确保 ORM 模型被导入，create_all 才能建表
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时建表。开发阶段用 create_all，稳定后再引入 Alembic。"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="伴行·时序 API",
    description="基于个人生活基线与可信数据分析的主动关怀系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/", tags=["健康检查"])
def health_check():
    return {"status": "ok", "service": "Companion Lite API"}
