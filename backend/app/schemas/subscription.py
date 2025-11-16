from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionTier, SubscriptionStatus


class SubscriptionCreate(BaseModel):
    """구독 생성 스키마"""

    tier: SubscriptionTier
    payment_method_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    """구독 응답 스키마"""

    id: int
    user_id: int
    plan_id: int
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionPlanResponse(BaseModel):
    """구독 플랜 응답 스키마"""

    id: int
    name: str
    tier: SubscriptionTier
    price: float
    max_papers: int
    max_analyses_per_month: int
    max_comparison_papers: int
    features: Optional[str] = None

    class Config:
        from_attributes = True
