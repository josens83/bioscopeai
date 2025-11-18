"""
프로모션 코드 API 엔드포인트

마케팅 할인 코드 검증 및 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import json

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.promotion_code import PromotionCode, PromotionCodeUsage
from app.services.promotion_service import PromotionCodeService, validate_promotion_code
from app.core.logging import app_logger as logger


router = APIRouter()


# ============================================================================
# Schemas
# ============================================================================

class PromotionCodeValidateRequest(BaseModel):
    """프로모션 코드 검증 요청"""
    code: str = Field(..., description="프로모션 코드")
    plan_id: Optional[str] = Field(None, description="적용하려는 플랜 ID")
    amount: Optional[float] = Field(None, description="구매 금액")

    @validator('code')
    def code_to_uppercase(cls, v):
        return v.upper()


class PromotionCodeValidateResponse(BaseModel):
    """프로모션 코드 검증 응답"""
    valid: bool
    code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    message: Optional[str] = None


class PromotionCodeUsageResponse(BaseModel):
    """프로모션 코드 사용 기록 응답"""
    id: int
    code: str
    discount_applied: float
    subscription_id: Optional[int]
    used_at: datetime

    class Config:
        from_attributes = True


class PromotionCodeResponse(BaseModel):
    """프로모션 코드 응답"""
    id: int
    code: str
    description: Optional[str]
    discount_type: str
    discount_value: float
    max_uses: Optional[int]
    max_uses_per_user: int
    min_purchase_amount: Optional[float]
    applicable_plans: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    is_active: bool
    uses_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PromotionCodeCreateRequest(BaseModel):
    """프로모션 코드 생성 요청"""
    code: str = Field(..., description="프로모션 코드 (대문자 권장)")
    description: Optional[str] = Field(None, description="코드 설명")
    discount_type: str = Field(..., description="할인 타입: percentage 또는 fixed")
    discount_value: float = Field(..., description="할인율(%) 또는 할인금액($)")
    max_uses: Optional[int] = Field(None, description="최대 사용 횟수")
    max_uses_per_user: int = Field(1, description="사용자당 최대 사용 횟수")
    min_purchase_amount: Optional[float] = Field(None, description="최소 구매 금액")
    applicable_plans: Optional[List[str]] = Field(None, description="적용 가능한 플랜 ID 목록")
    valid_from: datetime = Field(..., description="시작일")
    valid_until: Optional[datetime] = Field(None, description="종료일")

    @validator('code')
    def code_to_uppercase(cls, v):
        return v.upper()

    @validator('discount_type')
    def validate_discount_type(cls, v):
        if v not in ['percentage', 'fixed']:
            raise ValueError('discount_type은 percentage 또는 fixed여야 합니다')
        return v

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if v <= 0:
            raise ValueError('할인 값은 0보다 커야 합니다')
        if values.get('discount_type') == 'percentage' and v > 100:
            raise ValueError('퍼센트 할인은 100 이하여야 합니다')
        return v


class PromotionCodeUpdateRequest(BaseModel):
    """프로모션 코드 수정 요청"""
    description: Optional[str] = None
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = None
    min_purchase_amount: Optional[float] = None
    applicable_plans: Optional[List[str]] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class PromotionCodeStatisticsResponse(BaseModel):
    """프로모션 코드 통계 응답"""
    code: str
    total_uses: int
    unique_users: int
    total_discount: float
    is_active: bool
    is_valid: bool


# ============================================================================
# 사용자 엔드포인트
# ============================================================================

@router.post("/validate", response_model=PromotionCodeValidateResponse)
async def validate_code(
    request: PromotionCodeValidateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    프로모션 코드 검증

    사용자가 프로모션 코드를 입력했을 때 유효성 확인
    """
    valid, error_msg, promo_code = await validate_promotion_code(
        db=db,
        code=request.code,
        user_id=current_user.id,
        plan_id=request.plan_id,
        amount=request.amount,
    )

    if not valid:
        return PromotionCodeValidateResponse(
            valid=False,
            message=error_msg
        )

    return PromotionCodeValidateResponse(
        valid=True,
        code=promo_code.code,
        discount_type=promo_code.discount_type,
        discount_value=promo_code.discount_value,
        message="사용 가능한 프로모션 코드입니다"
    )


@router.get("/my-usage", response_model=List[PromotionCodeUsageResponse])
async def get_my_usage(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 프로모션 코드 사용 이력

    사용자가 사용한 모든 프로모션 코드 기록 조회
    """
    usages = await PromotionCodeService.get_user_usage_history(db, current_user.id)
    return usages


# ============================================================================
# 관리자 엔드포인트
# ============================================================================

@router.get("/admin/codes", response_model=List[PromotionCodeResponse])
async def list_promotion_codes(
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    [관리자] 모든 프로모션 코드 목록 조회

    필터링 옵션:
    - is_active: 활성화 상태로 필터링
    """
    query = select(PromotionCode).order_by(PromotionCode.created_at.desc())

    if is_active is not None:
        query = query.where(PromotionCode.is_active == is_active)

    result = await db.execute(query)
    codes = result.scalars().all()

    return codes


@router.post("/admin/codes", response_model=PromotionCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_promotion_code(
    code_data: PromotionCodeCreateRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    [관리자] 새 프로모션 코드 생성

    마케팅 캠페인용 할인 코드 생성
    """
    # 중복 코드 확인
    result = await db.execute(
        select(PromotionCode).where(PromotionCode.code == code_data.code)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 존재하는 프로모션 코드입니다: {code_data.code}"
        )

    # applicable_plans를 JSON으로 변환
    applicable_plans_json = None
    if code_data.applicable_plans:
        applicable_plans_json = json.dumps(code_data.applicable_plans)

    # 프로모션 코드 생성
    new_code = PromotionCode(
        code=code_data.code,
        description=code_data.description,
        discount_type=code_data.discount_type,
        discount_value=code_data.discount_value,
        max_uses=code_data.max_uses,
        max_uses_per_user=code_data.max_uses_per_user,
        min_purchase_amount=code_data.min_purchase_amount,
        applicable_plans=applicable_plans_json,
        valid_from=code_data.valid_from,
        valid_until=code_data.valid_until,
        is_active=True,
        uses_count=0,
        created_by=current_admin.id,
    )

    db.add(new_code)
    await db.commit()
    await db.refresh(new_code)

    logger.info(f"프로모션 코드 생성: {new_code.code} by admin {current_admin.id}")

    return new_code


@router.put("/admin/codes/{code_id}", response_model=PromotionCodeResponse)
async def update_promotion_code(
    code_id: int,
    code_data: PromotionCodeUpdateRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    [관리자] 프로모션 코드 수정

    코드 자체와 할인 값은 변경 불가 (사용 기록 무결성 보호)
    """
    # 프로모션 코드 조회
    result = await db.execute(
        select(PromotionCode).where(PromotionCode.id == code_id)
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로모션 코드를 찾을 수 없습니다"
        )

    # 수정 가능한 필드만 업데이트
    if code_data.description is not None:
        promo_code.description = code_data.description

    if code_data.max_uses is not None:
        promo_code.max_uses = code_data.max_uses

    if code_data.max_uses_per_user is not None:
        promo_code.max_uses_per_user = code_data.max_uses_per_user

    if code_data.min_purchase_amount is not None:
        promo_code.min_purchase_amount = code_data.min_purchase_amount

    if code_data.applicable_plans is not None:
        promo_code.applicable_plans = json.dumps(code_data.applicable_plans)

    if code_data.valid_until is not None:
        promo_code.valid_until = code_data.valid_until

    if code_data.is_active is not None:
        promo_code.is_active = code_data.is_active

    await db.commit()
    await db.refresh(promo_code)

    logger.info(f"프로모션 코드 수정: {promo_code.code} by admin {current_admin.id}")

    return promo_code


@router.delete("/admin/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion_code(
    code_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    [관리자] 프로모션 코드 삭제

    주의: 사용 기록이 있는 경우 삭제 대신 비활성화 권장
    """
    result = await db.execute(
        select(PromotionCode).where(PromotionCode.id == code_id)
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로모션 코드를 찾을 수 없습니다"
        )

    # 사용 기록 확인
    if promo_code.uses_count > 0:
        logger.warning(f"사용 기록이 있는 프로모션 코드 삭제 시도: {promo_code.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용 기록이 있는 프로모션 코드는 삭제할 수 없습니다. 비활성화를 권장합니다."
        )

    await db.delete(promo_code)
    await db.commit()

    logger.info(f"프로모션 코드 삭제: {promo_code.code} by admin {current_admin.id}")


@router.get("/admin/codes/{code_id}/statistics", response_model=PromotionCodeStatisticsResponse)
async def get_code_statistics(
    code_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    [관리자] 프로모션 코드 통계

    사용 횟수, 고유 사용자 수, 총 할인 금액 등
    """
    stats = await PromotionCodeService.get_code_statistics(db, code_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로모션 코드를 찾을 수 없습니다"
        )

    return stats


@router.get("/admin/codes/{code_id}/usages", response_model=List[PromotionCodeUsageResponse])
async def get_code_usages(
    code_id: int,
    limit: int = Query(100, description="조회할 최대 개수"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    [관리자] 프로모션 코드 사용 기록

    특정 코드의 모든 사용 이력 조회
    """
    result = await db.execute(
        select(PromotionCodeUsage)
        .where(PromotionCodeUsage.promotion_code_id == code_id)
        .order_by(PromotionCodeUsage.used_at.desc())
        .limit(limit)
    )
    usages = result.scalars().all()

    return usages
