"""
Usage Domain API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domains.auth.dependencies import get_db, get_current_user
from app.domains.auth.models import User
from .models import Usage

router = APIRouter()


@router.get("/my")
async def get_my_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's usage"""
    result = await db.execute(select(Usage).where(Usage.user_id == current_user.id))
    return result.scalars().all()
