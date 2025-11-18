"""
Admin Users Management API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domains.auth.dependencies import get_db, get_current_admin
from app.domains.auth.models import User

router = APIRouter()


@router.get("/")
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """List all users"""
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/stats")
async def user_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """User statistics"""
    total = await db.execute(select(func.count(User.id)))
    active = await db.execute(select(func.count(User.id)).where(User.is_active == True))
    verified = await db.execute(select(func.count(User.id)).where(User.is_verified == True))
    
    return {
        "total_users": total.scalar(),
        "active_users": active.scalar(),
        "verified_users": verified.scalar()
    }
