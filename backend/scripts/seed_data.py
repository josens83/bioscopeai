"""
데이터베이스 초기 데이터 생성 스크립트

Usage:
    python -m scripts.seed_data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.usage import PlanLimit
from app.models.subscription import SubscriptionPlan
from app.models.user import User
from app.core.security import get_password_hash
from app.core.logging import app_logger as logger


async def seed_plan_limits(db: AsyncSession):
    """플랜별 사용 제한 데이터 생성"""
    logger.info("🔧 플랜 제한 데이터 생성 중...")

    # 기존 데이터 확인
    result = await db.execute(select(PlanLimit))
    existing = result.scalars().all()

    if existing:
        logger.info(f"⏭️  이미 {len(existing)}개의 플랜 제한이 존재합니다.")
        return

    plans = [
        PlanLimit(
            plan_name="free",
            papers_per_month=10,
            rag_queries_per_month=50,
            api_calls_per_day=100,
            max_file_size_mb=5,
            pdf_export=False,
            priority_support=False
        ),
        PlanLimit(
            plan_name="basic",
            papers_per_month=100,
            rag_queries_per_month=500,
            api_calls_per_day=1000,
            max_file_size_mb=10,
            pdf_export=True,
            priority_support=False
        ),
        PlanLimit(
            plan_name="pro",
            papers_per_month=-1,  # unlimited
            rag_queries_per_month=-1,  # unlimited
            api_calls_per_day=10000,
            max_file_size_mb=50,
            pdf_export=True,
            priority_support=True
        )
    ]

    db.add_all(plans)
    await db.commit()
    logger.success(f"✅ {len(plans)}개의 플랜 제한 생성 완료")


async def seed_subscription_plans(db: AsyncSession):
    """구독 플랜 데이터 생성"""
    logger.info("🔧 구독 플랜 데이터 생성 중...")

    # 기존 데이터 확인
    result = await db.execute(select(SubscriptionPlan))
    existing = result.scalars().all()

    if existing:
        logger.info(f"⏭️  이미 {len(existing)}개의 구독 플랜이 존재합니다.")
        return

    plans = [
        SubscriptionPlan(
            tier="free",
            name="Free Plan",
            price=0.00,
            currency="usd",
            billing_cycle="monthly",
            stripe_price_id=None,  # Free plan has no Stripe price
            features={
                "papers_per_month": 10,
                "rag_queries": 50,
                "max_file_size": "5MB",
                "pdf_export": False,
                "priority_support": False,
                "api_access": True
            },
            is_active=True
        ),
        SubscriptionPlan(
            tier="basic",
            name="Basic Plan",
            price=19.99,
            currency="usd",
            billing_cycle="monthly",
            stripe_price_id="price_basic_monthly_placeholder",  # TODO: Stripe에서 실제 price_id로 교체 필요
            features={
                "papers_per_month": 100,
                "rag_queries": 500,
                "max_file_size": "10MB",
                "pdf_export": True,
                "priority_support": False,
                "api_access": True,
                "advanced_analytics": True
            },
            is_active=True
        ),
        SubscriptionPlan(
            tier="pro",
            name="Pro Plan",
            price=99.99,
            currency="usd",
            billing_cycle="monthly",
            stripe_price_id="price_pro_monthly_placeholder",  # TODO: Stripe에서 실제 price_id로 교체 필요
            features={
                "papers_per_month": "unlimited",
                "rag_queries": "unlimited",
                "max_file_size": "50MB",
                "pdf_export": True,
                "priority_support": True,
                "api_access": True,
                "advanced_analytics": True,
                "custom_models": True,
                "dedicated_support": True
            },
            is_active=True
        )
    ]

    db.add_all(plans)
    await db.commit()
    logger.success(f"✅ {len(plans)}개의 구독 플랜 생성 완료")
    logger.warning("⚠️  Stripe Price ID를 실제 값으로 업데이트해야 합니다!")


async def seed_demo_user(db: AsyncSession):
    """데모 사용자 계정 생성"""
    logger.info("🔧 데모 사용자 생성 중...")

    # 기존 사용자 확인
    result = await db.execute(
        select(User).where(User.email == "demo@bioscopeai.com")
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.info("⏭️  데모 사용자가 이미 존재합니다.")
        return

    demo_user = User(
        email="demo@bioscopeai.com",
        username="demo_user",
        hashed_password=get_password_hash("demo1234"),
        full_name="Demo User",
        is_active=True,
        is_verified=True,
        role="user"
    )

    db.add(demo_user)
    await db.commit()
    await db.refresh(demo_user)

    logger.success("✅ 데모 사용자 생성 완료")
    logger.info("   📧 이메일: demo@bioscopeai.com")
    logger.info("   🔑 비밀번호: demo1234")


async def seed_admin_user(db: AsyncSession):
    """관리자 계정 생성"""
    logger.info("🔧 관리자 사용자 생성 중...")

    # 기존 관리자 확인
    result = await db.execute(
        select(User).where(User.email == "admin@bioscopeai.com")
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.info("⏭️  관리자 사용자가 이미 존재합니다.")
        return

    admin_user = User(
        email="admin@bioscopeai.com",
        username="admin",
        hashed_password=get_password_hash("admin1234"),
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        role="admin"
    )

    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)

    logger.success("✅ 관리자 사용자 생성 완료")
    logger.info("   📧 이메일: admin@bioscopeai.com")
    logger.info("   🔑 비밀번호: admin1234")
    logger.warning("   ⚠️  프로덕션 환경에서는 반드시 비밀번호를 변경하세요!")


async def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("🚀 BioscopeAI 데이터베이스 초기 데이터 생성")
    logger.info("=" * 60)

    try:
        async with async_session_maker() as db:
            # 1. 플랜 제한 생성
            await seed_plan_limits(db)

            # 2. 구독 플랜 생성
            await seed_subscription_plans(db)

            # 3. 데모 사용자 생성
            await seed_demo_user(db)

            # 4. 관리자 사용자 생성
            await seed_admin_user(db)

        logger.info("=" * 60)
        logger.success("✅ 모든 초기 데이터 생성 완료!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📋 다음 단계:")
        logger.info("   1. Stripe 대시보드에서 Price ID를 생성하세요")
        logger.info("   2. subscription_plans 테이블의 stripe_price_id를 업데이트하세요")
        logger.info("   3. 프로덕션 환경에서는 admin 비밀번호를 변경하세요")
        logger.info("")

    except Exception as e:
        logger.error(f"❌ 데이터 생성 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
