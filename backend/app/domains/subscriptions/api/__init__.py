"""
Subscriptions API - 분할된 라우터
"""
from fastapi import APIRouter
from . import plans, checkout, webhooks

router = APIRouter()

# 서브 라우터 포함
router.include_router(plans.router, tags=["plans"])
router.include_router(checkout.router, prefix="/checkout", tags=["checkout"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
