"""
GDPR 데이터 내보내기 서비스

사용자의 모든 개인 데이터를 내보내기 (GDPR 규정 준수)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.paper import Paper
from app.models.analysis import Analysis
from app.models.subscription import Subscription
from app.models.usage import Usage
from app.models.audit_log import AuditLog
from datetime import datetime
from typing import Dict, Any
import json


class DataExportService:
    """사용자 데이터 내보내기 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_user_data(self, user: User) -> Dict[str, Any]:
        """
        사용자의 모든 개인 데이터를 JSON 형식으로 내보내기

        GDPR Article 20 - Right to data portability 준수
        """
        # 기본 프로필 정보
        user_profile = await self._export_user_profile(user)

        # 논문 데이터
        papers = await self._export_papers(user)

        # 분석 히스토리
        analyses = await self._export_analyses(user)

        # 구독 정보
        subscriptions = await self._export_subscriptions(user)

        # 사용량 기록
        usage_history = await self._export_usage_history(user)

        # 감사 로그 (사용자 관련)
        audit_logs = await self._export_audit_logs(user)

        return {
            "export_info": {
                "exported_at": datetime.utcnow().isoformat(),
                "user_id": user.id,
                "format": "JSON",
                "gdpr_compliant": True,
            },
            "user_profile": user_profile,
            "papers": papers,
            "analyses": analyses,
            "subscriptions": subscriptions,
            "usage_history": usage_history,
            "audit_logs": audit_logs,
        }

    async def _export_user_profile(self, user: User) -> Dict[str, Any]:
        """사용자 프로필 정보 내보내기"""
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "verified_at": user.verified_at.isoformat() if user.verified_at else None,
        }

    async def _export_papers(self, user: User) -> list:
        """사용자가 업로드한 논문 목록"""
        result = await self.db.execute(
            select(Paper).where(Paper.user_id == user.id).order_by(Paper.created_at.desc())
        )
        papers = result.scalars().all()

        return [
            {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "publication_date": paper.publication_date.isoformat() if paper.publication_date else None,
                "doi": paper.doi,
                "pmid": paper.pmid,
                "keywords": paper.keywords,
                "source": paper.source,
                "created_at": paper.created_at.isoformat() if paper.created_at else None,
            }
            for paper in papers
        ]

    async def _export_analyses(self, user: User) -> list:
        """사용자의 분석 히스토리"""
        result = await self.db.execute(
            select(Analysis).where(Analysis.user_id == user.id).order_by(Analysis.created_at.desc())
        )
        analyses = result.scalars().all()

        return [
            {
                "id": analysis.id,
                "analysis_type": analysis.analysis_type.value if analysis.analysis_type else None,
                "paper_id": analysis.paper_id,
                "query": analysis.query,
                "result": analysis.result,
                "metadata": analysis.metadata,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            }
            for analysis in analyses
        ]

    async def _export_subscriptions(self, user: User) -> list:
        """사용자의 구독 정보"""
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user.id).order_by(Subscription.created_at.desc())
        )
        subscriptions = result.scalars().all()

        return [
            {
                "id": subscription.id,
                "plan_id": subscription.plan_id,
                "status": subscription.status.value if subscription.status else None,
                "stripe_subscription_id": subscription.stripe_subscription_id,
                "stripe_customer_id": subscription.stripe_customer_id,
                "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
                "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
                "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None,
            }
            for subscription in subscriptions
        ]

    async def _export_usage_history(self, user: User) -> list:
        """사용자의 사용량 기록"""
        result = await self.db.execute(
            select(Usage).where(Usage.user_id == user.id).order_by(Usage.year.desc(), Usage.month.desc())
        )
        usage_records = result.scalars().all()

        return [
            {
                "year": usage.year,
                "month": usage.month,
                "papers_analyzed": usage.papers_analyzed,
                "rag_queries": usage.rag_queries,
                "summaries_generated": usage.summaries_generated,
                "comparisons_made": usage.comparisons_made,
                "pdf_exports": usage.pdf_exports,
                "api_calls": usage.api_calls,
            }
            for usage in usage_records
        ]

    async def _export_audit_logs(self, user: User) -> list:
        """사용자 관련 감사 로그"""
        result = await self.db.execute(
            select(AuditLog).where(AuditLog.user_id == user.id).order_by(AuditLog.created_at.desc()).limit(1000)
        )
        audit_logs = result.scalars().all()

        return [
            {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "changes": log.changes,
                "metadata": log.metadata,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_logs
        ]


async def export_user_data_json(db: AsyncSession, user: User) -> str:
    """
    사용자 데이터를 JSON 문자열로 내보내기

    Args:
        db: 데이터베이스 세션
        user: 내보낼 사용자

    Returns:
        JSON 형식의 사용자 데이터
    """
    service = DataExportService(db)
    data = await service.export_user_data(user)
    return json.dumps(data, ensure_ascii=False, indent=2)
