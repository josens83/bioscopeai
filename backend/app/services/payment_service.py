from typing import Optional
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Stripe 결제 서비스"""

    def create_customer(self, email: str, name: Optional[str] = None) -> str:
        """Stripe 고객 생성"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
            )
            return customer.id
        except stripe.error.StripeError as e:
            print(f"Stripe 고객 생성 오류: {e}")
            raise

    def create_subscription(
        self, customer_id: str, price_id: str
    ) -> dict:
        """구독 생성"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
            )

            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status,
            }

        except stripe.error.StripeError as e:
            print(f"구독 생성 오류: {e}")
            raise

    def cancel_subscription(
        self, subscription_id: str, at_period_end: bool = True
    ) -> dict:
        """구독 취소"""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }

        except stripe.error.StripeError as e:
            print(f"구독 취소 오류: {e}")
            raise

    def get_subscription(self, subscription_id: str) -> Optional[dict]:
        """구독 정보 조회"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }
        except stripe.error.StripeError as e:
            print(f"구독 조회 오류: {e}")
            return None

    def create_checkout_session(
        self, customer_id: str, price_id: str, success_url: str, cancel_url: str
    ) -> dict:
        """Checkout 세션 생성"""
        try:
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
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return {
                "session_id": checkout_session.id,
                "url": checkout_session.url,
            }

        except stripe.error.StripeError as e:
            print(f"Checkout 세션 생성 오류: {e}")
            raise

    def construct_webhook_event(self, payload: bytes, sig_header: str):
        """웹훅 이벤트 검증 및 구성"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            print(f"잘못된 페이로드: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            print(f"잘못된 서명: {e}")
            raise


# 싱글톤 인스턴스
payment_service = PaymentService()
