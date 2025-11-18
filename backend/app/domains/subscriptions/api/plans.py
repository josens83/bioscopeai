"""
Subscription Plans API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domains.auth.dependencies import get_db
from ..models import SubscriptionPlan

router = APIRouter()


@router.get("/plans")
async def get_plans(db: AsyncSession = Depends(get_db)):
    """Get all subscription plans"""
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.is_active == True))
    return result.scalars().all()
