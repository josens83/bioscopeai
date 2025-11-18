"""
프로모션 코드 서비스

할인 코드 검증, 적용 및 사용 기록 관리
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import json
import stripe

from app.models.promotion_code import PromotionCode, PromotionCodeUsage
from app.models.user import User
from app.core.config import settings
from app.core.logging import app_logger as logger

stripe.api_key = settings.STRIPE_SECRET_KEY


class PromotionCodeService:
    """프로모션 코드 관리 서비스"""

    @staticmethod
    async def validate_code(
        db: AsyncSession,
        code: str,
        user_id: int,
        plan_id: Optional[str] = None,
        amount: Optional[float] = None,
    ) -> Tuple[bool, Optional[str], Optional[PromotionCode]]:
        """
        프로모션 코드 검증

        Args:
            db: 데이터베이스 세션
            code: 프로모션 코드
            user_id: 사용자 ID
            plan_id: 적용하려는 플랜 ID (선택)
            amount: 구매 금액 (선택)

        Returns:
            (유효 여부, 에러 메시지, 프로모션 코드 객체)
        """
        # 코드 조회
        result = await db.execute(
            select(PromotionCode).where(PromotionCode.code == code.upper())
        )
        promo_code = result.scalar_one_or_none()

        if not promo_code:
            return False, "존재하지 않는 프로모션 코드입니다", None

        # 활성화 상태 확인
        if not promo_code.is_active:
            return False, "비활성화된 프로모션 코드입니다", None

        # 유효 기간 확인
        now = datetime.utcnow()
        if promo_code.valid_from and now < promo_code.valid_from.replace(tzinfo=None):
            return False, "아직 사용할 수 없는 프로모션 코드입니다", None

        if promo_code.valid_until and now > promo_code.valid_until.replace(tzinfo=None):
            return False, "만료된 프로모션 코드입니다", None

        # 전체 사용 횟수 확인
        if promo_code.max_uses and promo_code.uses_count >= promo_code.max_uses:
            return False, "사용 가능 횟수를 초과한 프로모션 코드입니다", None

        # 사용자별 사용 횟수 확인
        usage_count_result = await db.execute(
            select(func.count(PromotionCodeUsage.id)).where(
                and_(
                    PromotionCodeUsage.promotion_code_id == promo_code.id,
                    PromotionCodeUsage.user_id == user_id
                )
            )
        )
        user_usage_count = usage_count_result.scalar()

        if user_usage_count >= promo_code.max_uses_per_user:
            return False, "이미 사용한 프로모션 코드입니다", None

        # 최소 구매 금액 확인
        if promo_code.min_purchase_amount and amount:
            if amount < promo_code.min_purchase_amount:
                return False, f"최소 구매 금액 ${promo_code.min_purchase_amount} 이상이어야 합니다", None

        # 적용 가능한 플랜 확인
        if promo_code.applicable_plans and plan_id:
            try:
                applicable_plans = json.loads(promo_code.applicable_plans)
                if plan_id not in applicable_plans:
                    return False, "이 플랜에는 사용할 수 없는 프로모션 코드입니다", None
            except json.JSONDecodeError:
                logger.error(f"프로모션 코드 {code}의 applicable_plans JSON 파싱 오류")

        return True, None, promo_code

    @staticmethod
    async def calculate_discount(
        promo_code: PromotionCode,
        original_amount: float
    ) -> float:
        """
        할인 금액 계산

        Args:
            promo_code: 프로모션 코드 객체
            original_amount: 원래 금액

        Returns:
            할인 금액
        """
        if promo_code.discount_type == "percentage":
            # 퍼센트 할인
            discount = original_amount * (promo_code.discount_value / 100)
        elif promo_code.discount_type == "fixed":
            # 고정 금액 할인
            discount = min(promo_code.discount_value, original_amount)
        else:
            logger.error(f"알 수 없는 할인 타입: {promo_code.discount_type}")
            discount = 0

        return round(discount, 2)

    @staticmethod
    async def apply_to_stripe_subscription(
        promo_code: PromotionCode,
        customer_id: str,
        price_id: str
    ) -> Dict[str, Any]:
        """
        Stripe 구독에 프로모션 코드 적용

        Args:
            promo_code: 프로모션 코드 객체
            customer_id: Stripe 고객 ID
            price_id: Stripe 가격 ID

        Returns:
            Stripe 구독 생성 결과
        """
        try:
            # Stripe에서 프로모션 코드 생성 또는 쿠폰 적용
            if promo_code.discount_type == "percentage":
                # 퍼센트 할인 쿠폰 생성
                coupon = stripe.Coupon.create(
                    percent_off=promo_code.discount_value,
                    duration="once",  # 첫 결제에만 적용
                    name=promo_code.code,
                )
            else:
                # 고정 금액 할인 쿠폰 생성
                coupon = stripe.Coupon.create(
                    amount_off=int(promo_code.discount_value * 100),  # cents 단위
                    currency="usd",
                    duration="once",
                    name=promo_code.code,
                )

            # 구독 생성 시 쿠폰 적용
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                coupon=coupon.id,
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
            )

            logger.info(f"프로모션 코드 {promo_code.code} 적용된 구독 생성: {subscription.id}")

            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status,
                "discount_applied": True,
                "coupon_id": coupon.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe 프로모션 코드 적용 오류: {e}")
            raise

    @staticmethod
    async def apply_to_checkout_session(
        promo_code: PromotionCode,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Stripe Checkout 세션에 프로모션 코드 적용

        Args:
            promo_code: 프로모션 코드 객체
            customer_id: Stripe 고객 ID
            price_id: Stripe 가격 ID
            success_url: 성공 URL
            cancel_url: 취소 URL

        Returns:
            Checkout 세션 정보
        """
        try:
            # Stripe에서 프로모션 코드 생성
            if promo_code.discount_type == "percentage":
                coupon = stripe.Coupon.create(
                    percent_off=promo_code.discount_value,
                    duration="once",
                    name=promo_code.code,
                )
            else:
                coupon = stripe.Coupon.create(
                    amount_off=int(promo_code.discount_value * 100),
                    currency="usd",
                    duration="once",
                    name=promo_code.code,
                )

            # Checkout 세션 생성
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                discounts=[{"coupon": coupon.id}],
                success_url=success_url,
                cancel_url=cancel_url,
            )

            logger.info(f"프로모션 코드 {promo_code.code} 적용된 체크아웃 세션 생성: {checkout_session.id}")

            return {
                "session_id": checkout_session.id,
                "url": checkout_session.url,
                "coupon_id": coupon.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe 체크아웃 프로모션 코드 적용 오류: {e}")
            raise

    @staticmethod
    async def record_usage(
        db: AsyncSession,
        promo_code: PromotionCode,
        user_id: int,
        discount_applied: float,
        subscription_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> PromotionCodeUsage:
        """
        프로모션 코드 사용 기록

        Args:
            db: 데이터베이스 세션
            promo_code: 프로모션 코드 객체
            user_id: 사용자 ID
            discount_applied: 실제 적용된 할인 금액
            subscription_id: 구독 ID (선택)
            ip_address: IP 주소 (선택)

        Returns:
            사용 기록 객체
        """
        # 사용 기록 생성
        usage = PromotionCodeUsage(
            promotion_code_id=promo_code.id,
            code=promo_code.code,
            user_id=user_id,
            subscription_id=subscription_id,
            discount_applied=discount_applied,
            ip_address=ip_address,
        )
        db.add(usage)

        # 프로모션 코드 사용 횟수 증가
        promo_code.uses_count += 1

        await db.commit()
        await db.refresh(usage)

        logger.info(f"프로모션 코드 사용 기록: code={promo_code.code}, user_id={user_id}, discount=${discount_applied}")

        return usage

    @staticmethod
    async def get_user_usage_history(
        db: AsyncSession,
        user_id: int
    ) -> list[PromotionCodeUsage]:
        """
        사용자의 프로모션 코드 사용 이력 조회

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            사용 이력 목록
        """
        result = await db.execute(
            select(PromotionCodeUsage)
            .where(PromotionCodeUsage.user_id == user_id)
            .order_by(PromotionCodeUsage.used_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_code_statistics(
        db: AsyncSession,
        code_id: int
    ) -> Dict[str, Any]:
        """
        프로모션 코드 통계 조회

        Args:
            db: 데이터베이스 세션
            code_id: 프로모션 코드 ID

        Returns:
            통계 정보
        """
        # 프로모션 코드 조회
        result = await db.execute(
            select(PromotionCode).where(PromotionCode.id == code_id)
        )
        promo_code = result.scalar_one_or_none()

        if not promo_code:
            return {}

        # 사용 기록 조회
        usage_result = await db.execute(
            select(PromotionCodeUsage).where(PromotionCodeUsage.promotion_code_id == code_id)
        )
        usages = usage_result.scalars().all()

        # 통계 계산
        total_discount = sum(usage.discount_applied for usage in usages)
        unique_users = len(set(usage.user_id for usage in usages))

        return {
            "code": promo_code.code,
            "total_uses": promo_code.uses_count,
            "unique_users": unique_users,
            "total_discount": total_discount,
            "is_active": promo_code.is_active,
            "is_valid": promo_code.is_valid,
        }


# 편의 함수들
async def validate_promotion_code(
    db: AsyncSession,
    code: str,
    user_id: int,
    plan_id: Optional[str] = None,
    amount: Optional[float] = None
) -> Tuple[bool, Optional[str], Optional[PromotionCode]]:
    """프로모션 코드 검증 편의 함수"""
    return await PromotionCodeService.validate_code(db, code, user_id, plan_id, amount)


async def apply_promotion_code(
    db: AsyncSession,
    promo_code: PromotionCode,
    user_id: int,
    original_amount: float,
    subscription_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> Tuple[float, PromotionCodeUsage]:
    """
    프로모션 코드 적용 및 기록

    Returns:
        (할인 금액, 사용 기록)
    """
    discount = await PromotionCodeService.calculate_discount(promo_code, original_amount)
    usage = await PromotionCodeService.record_usage(
        db, promo_code, user_id, discount, subscription_id, ip_address
    )
    return discount, usage
