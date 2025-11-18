"""
이용약관 및 개인정보 처리방침 API

법적 요구사항 준수를 위한 약관 동의 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.terms_acceptance import TermsAcceptance, TermsVersion
from app.core.logging import app_logger as logger


router = APIRouter()


# Schemas
class TermsVersionResponse(BaseModel):
    """약관 버전 정보"""
    id: int
    terms_type: str
    version: str
    language: str
    title: str
    content: str
    is_required: bool
    effective_date: datetime

    class Config:
        from_attributes = True


class TermsAcceptanceRequest(BaseModel):
    """약관 동의 요청"""
    terms_type: str = Field(..., description="약관 유형 (terms_of_service, privacy_policy, marketing)")
    version: str = Field(..., description="약관 버전")
    accepted: bool = Field(..., description="동의 여부")


class TermsAcceptanceResponse(BaseModel):
    """약관 동의 응답"""
    id: int
    terms_type: str
    version: str
    accepted: bool
    accepted_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/current", response_model=List[TermsVersionResponse])
async def get_current_terms(
    language: str = "ko",
    db: AsyncSession = Depends(get_db),
):
    """
    현재 유효한 약관 목록 조회

    회원가입 시 또는 약관 확인 시 사용
    """
    result = await db.execute(
        select(TermsVersion).where(
            and_(
                TermsVersion.is_active == True,
                TermsVersion.language == language
            )
        ).order_by(TermsVersion.terms_type)
    )
    terms = result.scalars().all()

    return terms


@router.post("/accept", response_model=TermsAcceptanceResponse, status_code=status.HTTP_201_CREATED)
async def accept_terms(
    request: Request,
    acceptance_data: TermsAcceptanceRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    약관 동의 처리

    사용자가 특정 버전의 약관에 동의하거나 철회
    """
    # 기존 동의 기록 확인
    result = await db.execute(
        select(TermsAcceptance).where(
            and_(
                TermsAcceptance.user_id == current_user.id,
                TermsAcceptance.terms_type == acceptance_data.terms_type,
                TermsAcceptance.version == acceptance_data.version
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # 업데이트
        existing.accepted = acceptance_data.accepted
        existing.accepted_at = datetime.utcnow() if acceptance_data.accepted else None
        existing.ip_address = request.client.host if request.client else None
        existing.user_agent = request.headers.get("User-Agent")
        await db.commit()
        await db.refresh(existing)

        logger.info(f"약관 동의 업데이트: user_id={current_user.id}, type={acceptance_data.terms_type}, accepted={acceptance_data.accepted}")
        return existing
    else:
        # 새로 생성
        new_acceptance = TermsAcceptance(
            user_id=current_user.id,
            terms_type=acceptance_data.terms_type,
            version=acceptance_data.version,
            accepted=acceptance_data.accepted,
            accepted_at=datetime.utcnow() if acceptance_data.accepted else None,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
        )
        db.add(new_acceptance)
        await db.commit()
        await db.refresh(new_acceptance)

        logger.info(f"약관 동의 생성: user_id={current_user.id}, type={acceptance_data.terms_type}, accepted={acceptance_data.accepted}")
        return new_acceptance


@router.get("/my-acceptances", response_model=List[TermsAcceptanceResponse])
async def get_my_acceptances(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 약관 동의 이력 조회

    사용자가 동의한 모든 약관 목록
    """
    result = await db.execute(
        select(TermsAcceptance).where(
            TermsAcceptance.user_id == current_user.id
        ).order_by(TermsAcceptance.created_at.desc())
    )
    acceptances = result.scalars().all()

    return acceptances


@router.get("/check-required")
async def check_required_acceptance(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    필수 약관 동의 여부 확인

    미동의한 필수 약관이 있으면 목록 반환
    """
    # 현재 활성 필수 약관 조회
    result = await db.execute(
        select(TermsVersion).where(
            and_(
                TermsVersion.is_active == True,
                TermsVersion.is_required == True
            )
        )
    )
    required_terms = result.scalars().all()

    # 사용자의 동의 기록 조회
    result = await db.execute(
        select(TermsAcceptance).where(
            and_(
                TermsAcceptance.user_id == current_user.id,
                TermsAcceptance.accepted == True
            )
        )
    )
    user_acceptances = result.scalars().all()

    # 동의한 약관 타입과 버전 세트
    accepted_set = {(acc.terms_type, acc.version) for acc in user_acceptances}

    # 미동의 필수 약관 찾기
    missing_terms = []
    for term in required_terms:
        if (term.terms_type, term.version) not in accepted_set:
            missing_terms.append({
                "terms_type": term.terms_type,
                "version": term.version,
                "title": term.title,
                "content": term.content,
            })

    return {
        "all_accepted": len(missing_terms) == 0,
        "missing_terms": missing_terms
    }
