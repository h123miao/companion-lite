"""汇总 v1 版本的所有路由。

第一个模块只挂载 auth 和 checkins，
其余模块开发完成后在这里逐个加入。
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth, checkins, family, activities, devices, health, sync, care_events, feedback,
    baselines, dashboard,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(checkins.router)
api_router.include_router(family.router)
api_router.include_router(activities.router)
api_router.include_router(devices.router)
api_router.include_router(health.router)
api_router.include_router(sync.router)
api_router.include_router(care_events.router)
api_router.include_router(feedback.router)
api_router.include_router(baselines.router)
api_router.include_router(dashboard.router)
