from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionTier, SubscriptionStatus
from app.schemas.base import BaseDBSchema


class SubscriptionCreate(BaseModel):
    """구독 생성 스키마"""

    tier: SubscriptionTier = Field(..., description="구독 플랜 티어")
    payment_method_id: Optional[str] = Field(None, description="Stripe 결제 수단 ID")
    promotion_code: Optional[str] = Field(None, description="프로모션 코드 (선택)")


class SubscriptionResponse(BaseDBSchema):
    """구독 응답 스키마"""
    # id, created_at, updated_at 자동 상속

    user_id: int = Field(..., description="사용자 ID")
    plan_id: int = Field(..., description="플랜 ID")
    status: SubscriptionStatus = Field(..., description="구독 상태")
    current_period_start: Optional[datetime] = Field(None, description="현재 기간 시작일")
    current_period_end: Optional[datetime] = Field(None, description="현재 기간 종료일")
    cancel_at_period_end: bool = Field(default=False, description="기간 종료 시 취소 여부")


class SubscriptionPlanResponse(BaseDBSchema):
    """구독 플랜 응답 스키마"""
    # id, created_at, updated_at 자동 상속

    name: str = Field(..., description="플랜 이름")
    tier: SubscriptionTier = Field(..., description="플랜 티어")
    price: float = Field(..., description="가격 (USD)")
    max_papers: int = Field(..., description="최대 논문 저장 수")
    max_analyses_per_month: int = Field(..., description="월간 최대 분석 횟수")
    max_comparison_papers: int = Field(..., description="최대 비교 논문 수")
    features: Optional[str] = Field(None, description="기능 설명 (JSON)")
