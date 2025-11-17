"""
사용량 및 플랜 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.usage import PlanLimit
from app.services.usage_service import UsageService
from pydantic import BaseModel, Field
from typing import Optional, Union

router = APIRouter()


class UsageStatsResponse(BaseModel):
    """사용량 통계 응답 스키마"""
    period: str = Field(..., description="사용량 집계 기간 (YYYY-MM)", example="2024-01")
    plan: str = Field(..., description="현재 플랜", example="free")
    usage: dict = Field(..., description="사용량 상세")
    features: dict = Field(..., description="사용 가능한 기능")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "period": "2024-01",
                    "plan": "free",
                    "usage": {
                        "papers_analyzed": {
                            "current": 5,
                            "limit": 10,
                            "percentage": 50.0
                        },
                        "rag_queries": {
                            "current": 20,
                            "limit": 50,
                            "percentage": 40.0
                        },
                        "api_calls": {
                            "current": 45,
                            "limit": 100
                        }
                    },
                    "features": {
                        "max_file_size_mb": 5,
                        "pdf_export": False,
                        "priority_support": False
                    }
                }
            ]
        }
    }


class PlanLimitResponse(BaseModel):
    """플랜 제한 정보 응답 스키마"""
    id: int
    plan_name: str = Field(..., description="플랜 이름", example="free")
    papers_per_month: int = Field(..., description="월별 논문 분석 제한 (-1: 무제한)", example=10)
    rag_queries_per_month: int = Field(..., description="월별 RAG 쿼리 제한 (-1: 무제한)", example=50)
    api_calls_per_day: int = Field(..., description="일별 API 호출 제한", example=100)
    max_file_size_mb: int = Field(..., description="최대 파일 크기 (MB)", example=5)
    pdf_export: bool = Field(..., description="PDF 내보내기 가능 여부", example=False)
    priority_support: bool = Field(..., description="우선 지원 여부", example=False)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "plan_name": "free",
                    "papers_per_month": 10,
                    "rag_queries_per_month": 50,
                    "api_calls_per_day": 100,
                    "max_file_size_mb": 5,
                    "pdf_export": False,
                    "priority_support": False
                }
            ]
        }
    }


@router.get("/my-usage", response_model=UsageStatsResponse)
async def get_my_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 사용자의 월별 사용량 통계 조회

    - **period**: 집계 기간 (YYYY-MM)
    - **plan**: 현재 플랜 (free, basic, pro)
    - **usage**: 사용량 상세 (논문 분석, RAG 쿼리, API 호출)
    - **features**: 사용 가능한 기능
    """
    stats = await UsageService.get_usage_stats(db, current_user.id)
    return stats


@router.get("/plans", response_model=list[PlanLimitResponse])
async def get_all_plans(db: AsyncSession = Depends(get_db)):
    """
    모든 플랜의 제한 정보 조회

    사용자가 플랜을 선택할 때 각 플랜의 제한 사항을 확인할 수 있습니다.
    """
    result = await db.execute(select(PlanLimit))
    plans = result.scalars().all()

    # Boolean 변환
    response = []
    for plan in plans:
        plan_dict = {
            "id": plan.id,
            "plan_name": plan.plan_name,
            "papers_per_month": plan.papers_per_month,
            "rag_queries_per_month": plan.rag_queries_per_month,
            "api_calls_per_day": plan.api_calls_per_day,
            "max_file_size_mb": plan.max_file_size_mb,
            "pdf_export": bool(plan.pdf_export),
            "priority_support": bool(plan.priority_support)
        }
        response.append(plan_dict)

    return response


@router.get("/plans/{plan_name}", response_model=PlanLimitResponse)
async def get_plan_detail(plan_name: str, db: AsyncSession = Depends(get_db)):
    """
    특정 플랜의 상세 정보 조회

    - **plan_name**: 플랜 이름 (free, basic, pro)
    """
    result = await db.execute(
        select(PlanLimit).where(PlanLimit.plan_name == plan_name)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플랜 '{plan_name}'을 찾을 수 없습니다."
        )

    return {
        "id": plan.id,
        "plan_name": plan.plan_name,
        "papers_per_month": plan.papers_per_month,
        "rag_queries_per_month": plan.rag_queries_per_month,
        "api_calls_per_day": plan.api_calls_per_day,
        "max_file_size_mb": plan.max_file_size_mb,
        "pdf_export": bool(plan.pdf_export),
        "priority_support": bool(plan.priority_support)
    }


@router.post("/check-feature/{feature}")
async def check_feature_access(
    feature: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 기능 사용 가능 여부 확인

    - **feature**: 기능 이름 (pdf_export, priority_support)

    사용 가능하면 200 OK, 불가능하면 403 Forbidden 반환
    """
    await UsageService.check_feature_access(db, current_user.id, feature)
    return {"message": f"'{feature}' 기능을 사용할 수 있습니다.", "accessible": True}
