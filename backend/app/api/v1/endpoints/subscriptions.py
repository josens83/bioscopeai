from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionPlanResponse
from app.services.payment_service import payment_service
from app.services.promotion_service import validate_promotion_code, PromotionCodeService
from app.services.email_service import (
    send_payment_receipt_email,
    send_payment_failed_email,
    send_subscription_cancelled_email
)
from app.core.logging import app_logger as logger
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """구독 생성 (프로모션 코드 지원)"""
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

    # 프로모션 코드 검증 (제공된 경우)
    promo_code = None
    discount_applied = 0.0
    if subscription_in.promotion_code:
        valid, error_msg, promo_code = await validate_promotion_code(
            db=db,
            code=subscription_in.promotion_code,
            user_id=current_user.id,
            plan_id=str(plan.id),
            amount=plan.price,
        )

        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg or "유효하지 않은 프로모션 코드입니다",
            )

        # 할인 금액 계산
        discount_applied = await PromotionCodeService.calculate_discount(
            promo_code, plan.price
        )

    # Stripe 고객 생성 (없는 경우)
    stripe_customer_id = None
    if not hasattr(current_user, "stripe_customer_id") or not current_user.stripe_customer_id:
        stripe_customer_id = payment_service.create_customer(
            email=current_user.email,
            name=current_user.full_name,
        )

    # Stripe 구독 생성 (프로모션 코드가 있으면 적용)
    if promo_code:
        stripe_result = await PromotionCodeService.apply_to_stripe_subscription(
            promo_code=promo_code,
            customer_id=stripe_customer_id,
            price_id=plan.stripe_price_id,
        )
    else:
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

    # 프로모션 코드 사용 기록
    if promo_code:
        ip_address = request.client.host if request.client else None
        await PromotionCodeService.record_usage(
            db=db,
            promo_code=promo_code,
            user_id=current_user.id,
            discount_applied=discount_applied,
            subscription_id=subscription.id,
            ip_address=ip_address,
        )
        logger.info(f"프로모션 코드 적용: {promo_code.code}, user_id={current_user.id}, discount=${discount_applied}")

    return {
        "subscription_id": subscription.id,
        "client_secret": stripe_result["client_secret"],
        "status": stripe_result["status"],
        "promotion_applied": promo_code is not None,
        "discount_amount": discount_applied if promo_code else 0,
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
    """
    Stripe 웹훅 처리

    처리하는 이벤트:
    - invoice.payment_succeeded: 결제 성공 (영수증 발송)
    - invoice.payment_failed: 결제 실패 (알림 발송)
    - customer.subscription.updated: 구독 업데이트
    - customer.subscription.deleted: 구독 삭제
    - customer.subscription.created: 구독 생성
    - charge.refunded: 환불 처리
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = payment_service.construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.error(f"웹훅 검증 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    event_type = event["type"]
    logger.info(f"Stripe 웹훅 수신: {event_type}, ID: {event['id']}")

    try:
        # 이벤트 타입별 처리
        if event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(db, event["data"]["object"])

        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(db, event["data"]["object"])

        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(db, event["data"]["object"])

        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(db, event["data"]["object"])

        elif event_type == "customer.subscription.created":
            await handle_subscription_created(db, event["data"]["object"])

        elif event_type == "charge.refunded":
            await handle_charge_refunded(db, event["data"]["object"])

        else:
            logger.info(f"처리되지 않은 이벤트 타입: {event_type}")

        return {"status": "success", "event_type": event_type}

    except Exception as e:
        logger.error(f"웹훅 처리 중 오류: {event_type}, {e}", exc_info=True)
        # 웹훅은 실패해도 200을 반환해야 재전송을 방지
        return {"status": "error", "message": str(e)}


async def handle_payment_succeeded(db: AsyncSession, invoice: dict):
    """결제 성공 처리 - 영수증 이메일 발송"""
    customer_id = invoice["customer"]
    amount = invoice["amount_paid"] / 100  # cents to dollars
    currency = invoice["currency"]

    # 구독 조회
    result = await db.execute(
        select(Subscription).join(User).where(
            Subscription.stripe_customer_id == customer_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        user = subscription.user
        plan = subscription.plan

        # 영수증 이메일 발송
        try:
            await send_payment_receipt_email(
                email=user.email,
                username=user.username,
                plan_name=plan.tier,
                amount=amount,
                currency=currency,
                transaction_id=invoice["id"]
            )
            logger.info(f"결제 성공 영수증 발송: {user.email}, {plan.tier}, ${amount}")
        except Exception as e:
            logger.error(f"영수증 이메일 발송 실패: {e}")


async def handle_payment_failed(db: AsyncSession, invoice: dict):
    """결제 실패 처리 - 알림 이메일 발송"""
    customer_id = invoice["customer"]

    # 구독 조회
    result = await db.execute(
        select(Subscription).join(User).where(
            Subscription.stripe_customer_id == customer_id
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        user = subscription.user

        # 구독 상태 업데이트 (결제 실패 시 past_due)
        subscription.status = SubscriptionStatus.PAST_DUE
        await db.commit()

        # 실패 이메일 발송
        try:
            failure_reason = invoice.get("last_payment_error", {}).get("message", "결제 처리 중 오류가 발생했습니다")
            await send_payment_failed_email(
                email=user.email,
                username=user.username,
                reason=failure_reason
            )
            logger.warning(f"결제 실패 알림 발송: {user.email}, {failure_reason}")
        except Exception as e:
            logger.error(f"결제 실패 이메일 발송 실패: {e}")


async def handle_subscription_created(db: AsyncSession, stripe_subscription: dict):
    """구독 생성 처리"""
    logger.info(f"구독 생성: {stripe_subscription['id']}")
    # 이미 create_subscription API에서 처리하므로 로깅만


async def handle_subscription_updated(db: AsyncSession, stripe_subscription: dict):
    """구독 업데이트 처리"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        old_status = subscription.status
        new_status = stripe_subscription["status"]

        subscription.status = new_status
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription["current_period_end"]
        )

        # cancel_at_period_end 확인
        subscription.cancel_at_period_end = stripe_subscription.get("cancel_at_period_end", False)

        await db.commit()

        logger.info(f"구독 업데이트: {subscription.id}, {old_status} -> {new_status}")


async def handle_subscription_deleted(db: AsyncSession, stripe_subscription: dict):
    """구독 삭제(취소) 처리 - 이메일 발송"""
    result = await db.execute(
        select(Subscription).join(User).join(SubscriptionPlan).where(
            Subscription.stripe_subscription_id == stripe_subscription["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        user = subscription.user
        plan = subscription.plan

        subscription.status = SubscriptionStatus.CANCELED
        await db.commit()

        # 취소 이메일 발송
        try:
            await send_subscription_cancelled_email(
                email=user.email,
                username=user.username,
                plan_name=plan.tier
            )
            logger.info(f"구독 취소 알림 발송: {user.email}, {plan.tier}")
        except Exception as e:
            logger.error(f"구독 취소 이메일 발송 실패: {e}")


async def handle_charge_refunded(db: AsyncSession, charge: dict):
    """환불 처리"""
    amount_refunded = charge["amount_refunded"] / 100
    customer_id = charge["customer"]

    # 구독 조회
    result = await db.execute(
        select(Subscription).join(User).where(
            Subscription.stripe_customer_id == customer_id
        ).order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        user = subscription.user
        logger.info(f"환불 처리: {user.email}, ${amount_refunded}")

        # 환불 시 구독 취소
        subscription.status = SubscriptionStatus.CANCELED
        await db.commit()
