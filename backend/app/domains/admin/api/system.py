"""
Admin System Monitoring API
"""
from fastapi import APIRouter, Depends
from app.domains.auth.dependencies import get_current_admin
from app.domains.auth.models import User

router = APIRouter()


@router.get("/health")
async def system_health(admin: User = Depends(get_current_admin)):
    """System health check"""
    return {"status": "healthy"}
