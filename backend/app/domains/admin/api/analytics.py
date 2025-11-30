"""
Admin Analytics API
"""
from fastapi import APIRouter, Depends
from app.domains.auth.dependencies import get_current_admin
from app.domains.auth.models import User

router = APIRouter()


@router.get("/usage")
async def usage_analytics(admin: User = Depends(get_current_admin)):
    """Usage analytics"""
    return {"message": "Usage analytics"}
