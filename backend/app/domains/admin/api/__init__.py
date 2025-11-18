"""
Admin API - 분할된 라우터
"""
from fastapi import APIRouter
from . import users, metrics, analytics, system

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["admin-users"])
router.include_router(metrics.router, prefix="/metrics", tags=["admin-metrics"])
router.include_router(analytics.router, prefix="/analytics", tags=["admin-analytics"])
router.include_router(system.router, prefix="/system", tags=["admin-system"])
