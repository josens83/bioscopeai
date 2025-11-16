from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionPlanResponse
from app.services.payment_service import payment_service
from datetime import datetime

router = APIRouter()


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    """구독 플랜 목록"""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active == True)
    )
    plans = result.scalars().all()
    return plans


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_in: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """구독 생성"""
    # 플랜 조회
    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.tier == subscription_in.tier,
            SubscriptionPlan.is_active == True
        )
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="구독 플랜을 찾을 수 없습니다",
        )

    # 기존 활성 구독 확인
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    existing_subscription = result.scalar_one_or_none()

    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 활성 구독이 있습니다",
        )

    # Stripe 고객 생성 (없는 경우)
    stripe_customer_id = None
    if not hasattr(current_user, "stripe_customer_id") or not current_user.stripe_customer_id:
        stripe_customer_id = payment_service.create_customer(
            email=current_user.email,
            name=current_user.full_name,
        )

    # Stripe 구독 생성
    stripe_result = payment_service.create_subscription(
        customer_id=stripe_customer_id,
        price_id=plan.stripe_price_id,
    )

    # 구독 저장
    subscription = Subscription(
        user_id=current_user.id,
        plan_id=plan.id,
        stripe_subscription_id=stripe_result["subscription_id"],
        stripe_customer_id=stripe_customer_id,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.utcnow(),
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    return {
        "subscription_id": subscription.id,
        "client_secret": stripe_result["client_secret"],
        "status": stripe_result["status"],
    }


@router.get("/my", response_model=SubscriptionResponse)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """내 구독 정보"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="활성 구독이 없습니다",
        )

    return subscription


@router.post("/cancel", response_model=dict)
async def cancel_subscription(
    at_period_end: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """구독 취소"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="활성 구독이 없습니다",
        )

    # Stripe에서 취소
    stripe_result = payment_service.cancel_subscription(
        subscription_id=subscription.stripe_subscription_id,
        at_period_end=at_period_end,
    )

    # 구독 상태 업데이트
    if at_period_end:
        subscription.cancel_at_period_end = True
    else:
        subscription.status = SubscriptionStatus.CANCELED

    await db.commit()

    return {
        "message": "구독이 취소되었습니다",
        "cancel_at_period_end": at_period_end,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Stripe 웹훅 처리"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = payment_service.construct_webhook_event(payload, sig_header)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # 이벤트 타입별 처리
    if event["type"] == "customer.subscription.updated":
        subscription_data = event["data"]["object"]
        await update_subscription_from_stripe(db, subscription_data)

    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"]
        await cancel_subscription_from_stripe(db, subscription_data)

    return {"status": "success"}


async def update_subscription_from_stripe(db: AsyncSession, stripe_subscription: dict):
    """Stripe 구독 데이터로 DB 업데이트"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = stripe_subscription["status"]
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription["current_period_end"]
        )
        await db.commit()


async def cancel_subscription_from_stripe(db: AsyncSession, stripe_subscription: dict):
    """Stripe 구독 취소 처리"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = SubscriptionStatus.CANCELED
        await db.commit()
