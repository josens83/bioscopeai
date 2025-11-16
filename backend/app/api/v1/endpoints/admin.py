"""
관리자 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.models.analysis import Analysis
from app.models.subscription import Subscription
from datetime import datetime, timedelta

router = APIRouter()


def is_admin(current_user: User) -> bool:
    """관리자 권한 확인"""
    return current_user.is_superuser


@router.get("/stats")
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """전체 통계 조회 (관리자 전용)"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    # 사용자 통계
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()

    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar()

    # 논문 통계
    total_papers_result = await db.execute(select(func.count(Paper.id)))
    total_papers = total_papers_result.scalar()

    # 최근 24시간 내 논문
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_papers_result = await db.execute(
        select(func.count(Paper.id)).where(Paper.created_at >= last_24h)
    )
    recent_papers = recent_papers_result.scalar()

    # 분석 통계
    total_analyses_result = await db.execute(select(func.count(Analysis.id)))
    total_analyses = total_analyses_result.scalar()

    # 최근 24시간 내 분석
    recent_analyses_result = await db.execute(
        select(func.count(Analysis.id)).where(Analysis.created_at >= last_24h)
    )
    recent_analyses = recent_analyses_result.scalar()

    # 구독 통계
    total_subscriptions_result = await db.execute(select(func.count(Subscription.id)))
    total_subscriptions = total_subscriptions_result.scalar()

    active_subscriptions_result = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == "active")
    )
    active_subscriptions = active_subscriptions_result.scalar()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
        },
        "papers": {
            "total": total_papers,
            "last_24h": recent_papers,
        },
        "analyses": {
            "total": total_analyses,
            "last_24h": recent_analyses,
        },
        "subscriptions": {
            "total": total_subscriptions,
            "active": active_subscriptions,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자 목록 조회 (관리자 전용)"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        "total": len(users),
        "skip": skip,
        "limit": limit,
    }


@router.get("/recent-activity")
async def get_recent_activity(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """최근 활동 조회 (관리자 전용)"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    # 최근 논문
    recent_papers_result = await db.execute(
        select(Paper)
        .where(Paper.created_at >= time_threshold)
        .order_by(Paper.created_at.desc())
        .limit(10)
    )
    recent_papers = recent_papers_result.scalars().all()

    # 최근 분석
    recent_analyses_result = await db.execute(
        select(Analysis)
        .where(Analysis.created_at >= time_threshold)
        .order_by(Analysis.created_at.desc())
        .limit(10)
    )
    recent_analyses = recent_analyses_result.scalars().all()

    return {
        "time_range_hours": hours,
        "recent_papers": [
            {
                "id": paper.id,
                "title": paper.title,
                "user_id": paper.user_id,
                "created_at": paper.created_at.isoformat(),
            }
            for paper in recent_papers
        ],
        "recent_analyses": [
            {
                "id": analysis.id,
                "type": analysis.analysis_type.value,
                "user_id": analysis.user_id,
                "created_at": analysis.created_at.isoformat(),
            }
            for analysis in recent_analyses
        ],
    }
