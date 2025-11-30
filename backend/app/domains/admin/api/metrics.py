"""
Admin Business Metrics API
"""
from fastapi import APIRouter, Depends
from app.domains.auth.dependencies import get_current_admin
from app.domains.auth.models import User

router = APIRouter()


@router.get("/business")
async def business_metrics(admin: User = Depends(get_current_admin)):
    """Business metrics (MRR, ARPU, etc.)"""
    return {
        "mrr": 0,
        "arpu": 0,
        "churn_rate": 0
    }
