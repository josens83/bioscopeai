"""
관리자 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.audit_service import log_admin_action
from app.models.paper import Paper
from app.models.analysis import Analysis
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.usage import Usage
from datetime import datetime, timedelta
from typing import Optional

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


@router.get("/business-metrics")
async def get_business_metrics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    비즈니스 메트릭 조회 (관리자 전용)

    - MRR (Monthly Recurring Revenue)
    - 플랜별 사용자 분포
    - 신규 가입자 (기간별)
    - 활성 사용자 (DAU/MAU)
    - 전환율 (Free -> Paid)
    - 이탈률
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    time_threshold = datetime.utcnow() - timedelta(days=days)

    # MRR 계산 (활성 구독 합산)
    mrr_result = await db.execute(
        select(func.sum(SubscriptionPlan.price)).select_from(Subscription).join(
            SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id
        ).where(Subscription.status == SubscriptionStatus.ACTIVE)
    )
    mrr = mrr_result.scalar() or 0

    # 플랜별 구독 수
    plans_result = await db.execute(
        select(
            SubscriptionPlan.tier,
            func.count(Subscription.id)
        ).select_from(Subscription).join(
            SubscriptionPlan, Subscription.plan_id == SubscriptionPlan.id
        ).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).group_by(SubscriptionPlan.tier)
    )
    plan_distribution = {tier: count for tier, count in plans_result.all()}

    # Free 사용자 수 (구독 없는 사용자)
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()

    paid_users_result = await db.execute(
        select(func.count(distinct(Subscription.user_id))).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    paid_users = paid_users_result.scalar() or 0
    free_users = total_users - paid_users

    plan_distribution["free"] = free_users

    # 신규 가입자 (기간별)
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= time_threshold)
    )
    new_users = new_users_result.scalar()

    # DAU (오늘 활동한 사용자)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    dau_result = await db.execute(
        select(func.count(distinct(Analysis.user_id))).where(
            Analysis.created_at >= today
        )
    )
    dau = dau_result.scalar()

    # MAU (지난 30일 활동한 사용자)
    last_30_days = datetime.utcnow() - timedelta(days=30)
    mau_result = await db.execute(
        select(func.count(distinct(Analysis.user_id))).where(
            Analysis.created_at >= last_30_days
        )
    )
    mau = mau_result.scalar()

    # 전환율 (Free -> Paid)
    conversion_rate = (paid_users / total_users * 100) if total_users > 0 else 0

    # 이탈률 (기간 내 취소된 구독 / 총 활성 구독)
    churned_result = await db.execute(
        select(func.count(Subscription.id)).where(
            and_(
                Subscription.status == SubscriptionStatus.CANCELED,
                Subscription.updated_at >= time_threshold
            )
        )
    )
    churned = churned_result.scalar()

    active_subs_result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    active_subs = active_subs_result.scalar()

    churn_rate = (churned / (active_subs + churned) * 100) if (active_subs + churned) > 0 else 0

    # ARPU (Average Revenue Per User)
    arpu = (mrr / paid_users) if paid_users > 0 else 0

    return {
        "period_days": days,
        "revenue": {
            "mrr": float(mrr),
            "arpu": float(arpu),
            "currency": "USD"
        },
        "users": {
            "total": total_users,
            "free": free_users,
            "paid": paid_users,
            "new_in_period": new_users,
            "conversion_rate": round(conversion_rate, 2)
        },
        "engagement": {
            "dau": dau,
            "mau": mau,
            "dau_mau_ratio": round((dau / mau * 100) if mau > 0 else 0, 2)
        },
        "plan_distribution": plan_distribution,
        "churn": {
            "churned_subscriptions": churned,
            "churn_rate": round(churn_rate, 2)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/usage-analytics")
async def get_usage_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사용량 분석 (관리자 전용)

    - 총 사용량 (논문, RAG 쿼리)
    - 플랜별 평균 사용량
    - 제한 근접 사용자 수
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month

    # 이번 달 총 사용량
    total_usage_result = await db.execute(
        select(
            func.sum(Usage.papers_analyzed).label("total_papers"),
            func.sum(Usage.rag_queries).label("total_queries"),
            func.sum(Usage.api_calls).label("total_api_calls")
        ).where(
            and_(
                Usage.year == current_year,
                Usage.month == current_month
            )
        )
    )
    total_usage = total_usage_result.first()

    # 플랜별 평균 사용량
    # 복잡한 조인이므로 간소화된 버전
    avg_usage_result = await db.execute(
        select(
            func.avg(Usage.papers_analyzed).label("avg_papers"),
            func.avg(Usage.rag_queries).label("avg_queries")
        ).where(
            and_(
                Usage.year == current_year,
                Usage.month == current_month
            )
        )
    )
    avg_usage = avg_usage_result.first()

    # 사용량 많은 사용자 Top 10
    power_users_result = await db.execute(
        select(
            Usage.user_id,
            func.sum(Usage.papers_analyzed + Usage.rag_queries).label("total_activity")
        ).where(
            and_(
                Usage.year == current_year,
                Usage.month == current_month
            )
        ).group_by(Usage.user_id).order_by(func.sum(Usage.papers_analyzed + Usage.rag_queries).desc()).limit(10)
    )
    power_users = power_users_result.all()

    return {
        "period": f"{current_year}-{current_month:02d}",
        "total_usage": {
            "papers_analyzed": total_usage.total_papers or 0,
            "rag_queries": total_usage.total_queries or 0,
            "api_calls": total_usage.total_api_calls or 0
        },
        "average_usage": {
            "papers_per_user": round(avg_usage.avg_papers or 0, 2),
            "queries_per_user": round(avg_usage.avg_queries or 0, 2)
        },
        "power_users": [
            {
                "user_id": user_id,
                "total_activity": int(activity)
            }
            for user_id, activity in power_users
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/users/{user_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자 정지 (관리자 전용)"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    # 자기 자신을 정지할 수 없음
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 정지할 수 없습니다"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    user.is_active = False
    await db.commit()

    # 감사 로그 기록
    await log_admin_action(
        db=db,
        admin=current_user,
        action="user.suspended",
        target_user=user,
        description=f"관리자가 사용자를 정지시킴: {user.email}",
        request=request,
        changes={"old": {"is_active": True}, "new": {"is_active": False}},
    )

    from app.core.logging import app_logger as logger
    logger.warning(f"관리자 {current_user.id}가 사용자 {user_id} ({user.email})를 정지시켰습니다")

    return {"message": f"사용자 {user.email}이(가) 정지되었습니다"}


@router.post("/users/{user_id}/activate", status_code=status.HTTP_200_OK)
async def activate_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자 활성화 (관리자 전용)"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    user.is_active = True
    await db.commit()

    # 감사 로그 기록
    await log_admin_action(
        db=db,
        admin=current_user,
        action="user.activated",
        target_user=user,
        description=f"관리자가 사용자를 활성화함: {user.email}",
        request=request,
        changes={"old": {"is_active": False}, "new": {"is_active": True}},
    )

    from app.core.logging import app_logger as logger
    logger.info(f"관리자 {current_user.id}가 사용자 {user_id} ({user.email})를 활성화했습니다")

    return {"message": f"사용자 {user.email}이(가) 활성화되었습니다"}


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    request: Request,
    user_id: int,
    permanent: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사용자 삭제 (관리자 전용)

    - permanent=False: 소프트 삭제 (계정 비활성화)
    - permanent=True: 하드 삭제 (데이터베이스에서 완전 삭제)
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    # 자기 자신을 삭제할 수 없음
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 삭제할 수 없습니다"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    from app.core.logging import app_logger as logger

    if permanent:
        # 감사 로그 먼저 기록 (삭제 전에)
        await log_admin_action(
            db=db,
            admin=current_user,
            action="user.deleted_permanent",
            target_user=user,
            description=f"관리자가 사용자를 영구 삭제함: {user.email}",
            request=request,
            changes={"old": {"exists": True}, "new": {"exists": False}},
        )
        # 하드 삭제 (실제 삭제)
        user_email = user.email
        await db.delete(user)
        await db.commit()
        logger.critical(f"관리자 {current_user.id}가 사용자 {user_id} ({user_email})를 영구 삭제했습니다")
        return {"message": f"사용자 {user_email}이(가) 영구 삭제되었습니다"}
    else:
        # 소프트 삭제 (비활성화)
        user.is_active = False
        await db.commit()
        # 감사 로그 기록
        await log_admin_action(
            db=db,
            admin=current_user,
            action="user.deleted_soft",
            target_user=user,
            description=f"관리자가 사용자를 삭제(비활성화)함: {user.email}",
            request=request,
            changes={"old": {"is_active": True}, "new": {"is_active": False}},
        )
        logger.warning(f"관리자 {current_user.id}가 사용자 {user_id} ({user.email})를 삭제(비활성화)했습니다")
        return {"message": f"사용자 {user.email}이(가) 삭제되었습니다 (복구 가능)"}


@router.put("/users/{user_id}/role", status_code=status.HTTP_200_OK)
async def update_user_role(
    request: Request,
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자 역할 변경 (관리자 전용)"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role은 'user' 또는 'admin'이어야 합니다"
        )

    # 자기 자신의 역할을 변경할 수 없음
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신의 역할을 변경할 수 없습니다"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    old_role = user.role
    user.role = role
    user.is_superuser = (role == "admin")
    await db.commit()

    # 감사 로그 기록
    await log_admin_action(
        db=db,
        admin=current_user,
        action="user.role_changed",
        target_user=user,
        description=f"관리자가 사용자의 역할을 변경함: {old_role} -> {role}",
        request=request,
        changes={"old": {"role": old_role}, "new": {"role": role}},
    )

    from app.core.logging import app_logger as logger
    logger.info(f"관리자 {current_user.id}가 사용자 {user_id} ({user.email})의 역할을 {old_role} -> {role}로 변경했습니다")

    return {"message": f"사용자 {user.email}의 역할이 {role}(으)로 변경되었습니다"}
