"""
사용량 추적 및 제한 서비스
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from app.models.usage import Usage, PlanLimit
from app.models.user import User
from app.models.subscription import Subscription
from app.core.logging import app_logger as logger
from app.core.exceptions import UsageLimitExceeded, FeatureNotAvailable


class UsageService:
    """사용량 추적 및 제한 서비스"""

    @staticmethod
    async def get_current_usage(db: AsyncSession, user_id: int) -> Usage:
        """현재 월의 사용량 조회 (없으면 생성)"""
        now = datetime.utcnow()
        year = now.year
        month = now.month

        # 현재 월의 사용량 조회
        result = await db.execute(
            select(Usage).where(
                Usage.user_id == user_id,
                Usage.year == year,
                Usage.month == month
            )
        )
        usage = result.scalar_one_or_none()

        # 없으면 생성
        if not usage:
            usage = Usage(
                user_id=user_id,
                year=year,
                month=month,
                papers_analyzed=0,
                rag_queries=0,
                api_calls=0
            )
            db.add(usage)
            await db.commit()
            await db.refresh(usage)
            logger.info(f"새로운 사용량 레코드 생성: user_id={user_id}, {year}-{month}")

        return usage

    @staticmethod
    async def get_user_plan(db: AsyncSession, user_id: int) -> str:
        """사용자의 현재 플랜 조회"""
        # 활성 구독 조회
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            ).order_by(Subscription.created_at.desc())
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            return subscription.plan  # basic, pro
        return "free"

    @staticmethod
    async def get_plan_limits(db: AsyncSession, plan_name: str) -> PlanLimit:
        """플랜별 제한 조회"""
        result = await db.execute(
            select(PlanLimit).where(PlanLimit.plan_name == plan_name)
        )
        plan_limit = result.scalar_one_or_none()

        if not plan_limit:
            # 기본값 (free 플랜)
            result = await db.execute(
                select(PlanLimit).where(PlanLimit.plan_name == "free")
            )
            plan_limit = result.scalar_one_or_none()

        return plan_limit

    @staticmethod
    async def check_and_increment(
        db: AsyncSession,
        user_id: int,
        usage_type: str  # "paper", "rag_query", "api_call"
    ) -> bool:
        """
        사용량 확인 및 증가

        Returns:
            bool: 사용 가능하면 True, 제한 초과면 HTTPException 발생
        """
        # 현재 사용량 조회
        usage = await UsageService.get_current_usage(db, user_id)

        # 사용자 플랜 조회
        plan_name = await UsageService.get_user_plan(db, user_id)

        # 플랜 제한 조회
        plan_limit = await UsageService.get_plan_limits(db, plan_name)

        # 사용량 확인
        if usage_type == "paper":
            current = usage.papers_analyzed
            limit = plan_limit.papers_per_month
            usage.papers_analyzed += 1
        elif usage_type == "rag_query":
            current = usage.rag_queries
            limit = plan_limit.rag_queries_per_month
            usage.rag_queries += 1
        elif usage_type == "api_call":
            current = usage.api_calls
            limit = plan_limit.api_calls_per_day  # 일별 제한은 별도 처리 필요
            usage.api_calls += 1
        else:
            raise ValueError(f"Unknown usage_type: {usage_type}")

        # 제한 확인 (-1은 unlimited)
        if limit != -1 and current >= limit:
            logger.warning(
                f"사용량 제한 초과: user_id={user_id}, plan={plan_name}, "
                f"type={usage_type}, current={current}, limit={limit}"
            )
            raise UsageLimitExceeded(
                usage_type=usage_type,
                current=current,
                limit=limit,
                plan=plan_name
            )

        # 사용량 증가
        await db.commit()
        await db.refresh(usage)

        logger.info(
            f"사용량 증가: user_id={user_id}, type={usage_type}, "
            f"current={current + 1}/{limit if limit != -1 else 'unlimited'}"
        )

        return True

    @staticmethod
    async def get_usage_stats(db: AsyncSession, user_id: int) -> dict:
        """사용자의 현재 월 사용량 통계"""
        usage = await UsageService.get_current_usage(db, user_id)
        plan_name = await UsageService.get_user_plan(db, user_id)
        plan_limit = await UsageService.get_plan_limits(db, plan_name)

        return {
            "period": f"{usage.year}-{usage.month:02d}",
            "plan": plan_name,
            "usage": {
                "papers_analyzed": {
                    "current": usage.papers_analyzed,
                    "limit": plan_limit.papers_per_month if plan_limit.papers_per_month != -1 else "unlimited",
                    "percentage": (usage.papers_analyzed / plan_limit.papers_per_month * 100) if plan_limit.papers_per_month > 0 else 0
                },
                "rag_queries": {
                    "current": usage.rag_queries,
                    "limit": plan_limit.rag_queries_per_month if plan_limit.rag_queries_per_month != -1 else "unlimited",
                    "percentage": (usage.rag_queries / plan_limit.rag_queries_per_month * 100) if plan_limit.rag_queries_per_month > 0 else 0
                },
                "api_calls": {
                    "current": usage.api_calls,
                    "limit": plan_limit.api_calls_per_day if plan_limit.api_calls_per_day != -1 else "unlimited"
                }
            },
            "features": {
                "max_file_size_mb": plan_limit.max_file_size_mb,
                "pdf_export": bool(plan_limit.pdf_export),
                "priority_support": bool(plan_limit.priority_support)
            }
        }

    @staticmethod
    async def check_feature_access(db: AsyncSession, user_id: int, feature: str) -> bool:
        """특정 기능 접근 권한 확인"""
        plan_name = await UsageService.get_user_plan(db, user_id)
        plan_limit = await UsageService.get_plan_limits(db, plan_name)

        if feature == "pdf_export":
            if not plan_limit.pdf_export:
                raise FeatureNotAvailable(
                    feature="PDF 내보내기",
                    required_plan="Basic",
                    current_plan=plan_name
                )
        elif feature == "priority_support":
            if not plan_limit.priority_support:
                raise FeatureNotAvailable(
                    feature="우선 지원",
                    required_plan="Pro",
                    current_plan=plan_name
                )

        return True
