"""
데이터베이스 초기 데이터 seeding 스크립트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, init_db
from app.models.subscription import SubscriptionPlan, SubscriptionTier
from app.models.user import User
from app.core.security import get_password_hash


async def seed_subscription_plans(db: AsyncSession):
    """구독 플랜 초기 데이터"""
    plans = [
        {
            "name": "Free",
            "tier": SubscriptionTier.FREE,
            "price": 0.0,
            "stripe_price_id": None,
            "max_papers": 10,
            "max_analyses_per_month": 20,
            "max_comparison_papers": 2,
            "features": '{"basic_search": true, "pdf_upload": true, "basic_ai": true}',
            "is_active": True,
        },
        {
            "name": "Basic",
            "tier": SubscriptionTier.BASIC,
            "price": 9.99,
            "stripe_price_id": "price_basic_monthly",  # Stripe에서 생성 필요
            "max_papers": 50,
            "max_analyses_per_month": 100,
            "max_comparison_papers": 5,
            "features": '{"advanced_search": true, "pdf_upload": true, "advanced_ai": true, "export": true}',
            "is_active": True,
        },
        {
            "name": "Premium",
            "tier": SubscriptionTier.PREMIUM,
            "price": 29.99,
            "stripe_price_id": "price_premium_monthly",  # Stripe에서 생성 필요
            "max_papers": 200,
            "max_analyses_per_month": 500,
            "max_comparison_papers": 10,
            "features": '{"unlimited_search": true, "pdf_upload": true, "premium_ai": true, "export": true, "api_access": true, "priority_support": true}',
            "is_active": True,
        },
        {
            "name": "Enterprise",
            "tier": SubscriptionTier.ENTERPRISE,
            "price": 99.99,
            "stripe_price_id": "price_enterprise_monthly",  # Stripe에서 생성 필요
            "max_papers": 1000,
            "max_analyses_per_month": 2000,
            "max_comparison_papers": 10,
            "features": '{"unlimited_search": true, "pdf_upload": true, "enterprise_ai": true, "export": true, "api_access": true, "dedicated_support": true, "custom_models": true, "team_collaboration": true}',
            "is_active": True,
        },
    ]

    for plan_data in plans:
        plan = SubscriptionPlan(**plan_data)
        db.add(plan)

    await db.commit()
    print("✓ 구독 플랜 데이터 추가 완료")


async def seed_demo_user(db: AsyncSession):
    """데모 사용자 생성"""
    demo_user = User(
        email="demo@bioscopeai.com",
        username="demo",
        hashed_password=get_password_hash("demo1234"),
        full_name="Demo User",
        is_active=True,
        is_superuser=False,
    )
    db.add(demo_user)

    # 관리자 계정
    admin_user = User(
        email="admin@bioscopeai.com",
        username="admin",
        hashed_password=get_password_hash("admin1234"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )
    db.add(admin_user)

    await db.commit()
    print("✓ 데모 사용자 데이터 추가 완료")
    print("  - demo@bioscopeai.com / demo1234")
    print("  - admin@bioscopeai.com / admin1234")


async def main():
    """메인 실행 함수"""
    print("데이터베이스 초기화 시작...")

    # 데이터베이스 테이블 생성
    await init_db()
    print("✓ 데이터베이스 테이블 생성 완료")

    # 세션 생성
    async with AsyncSessionLocal() as db:
        try:
            await seed_subscription_plans(db)
            await seed_demo_user(db)
            print("\n✓ 모든 초기 데이터 추가 완료!")
        except Exception as e:
            print(f"✗ 오류 발생: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
