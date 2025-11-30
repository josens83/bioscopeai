"""
Usage Tracking 테스트
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.user import User
from app.models.usage import Usage, PlanLimit
from app.services.usage_service import UsageService
from app.core.exceptions import UsageLimitExceeded
from app.core.security import get_password_hash, create_access_token


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """테스트 사용자 생성"""
    user = User(
        email="usage_test@example.com",
        username="usagetest",
        hashed_password=get_password_hash("testpass123"),
        full_name="Usage Test User",
        is_active=True,
        is_verified=True,
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_plan_limits(db_session: AsyncSession):
    """테스트 플랜 제한 생성"""
    plans = [
        PlanLimit(
            plan_name="free",
            papers_per_month=10,
            rag_queries_per_month=50,
            api_calls_per_day=100,
            max_file_size_mb=5,
            pdf_export=False,
            priority_support=False,
        ),
        PlanLimit(
            plan_name="basic",
            papers_per_month=100,
            rag_queries_per_month=500,
            api_calls_per_day=1000,
            max_file_size_mb=10,
            pdf_export=True,
            priority_support=False,
        ),
        PlanLimit(
            plan_name="pro",
            papers_per_month=-1,  # unlimited
            rag_queries_per_month=-1,  # unlimited
            api_calls_per_day=10000,
            max_file_size_mb=50,
            pdf_export=True,
            priority_support=True,
        ),
    ]
    for plan in plans:
        db_session.add(plan)
    await db_session.commit()
    return plans


@pytest.fixture
def auth_headers(test_user: User):
    """인증 헤더 생성"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_current_usage_empty(
    client: AsyncClient, test_user: User, test_plan_limits, auth_headers
):
    """현재 사용량 조회 (데이터 없음)"""
    response = await client.get(
        "/api/v1/usage/current",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["papers_analyzed"] == 0
    assert data["rag_queries"] == 0
    assert data["api_calls"] == 0


@pytest.mark.asyncio
async def test_usage_tracking_increment(db_session: AsyncSession, test_user: User, test_plan_limits):
    """사용량 증가 테스트"""
    usage_service = UsageService(db_session)

    # 첫 번째 증가
    await usage_service.check_and_increment(test_user.id, "papers_analyzed", "free")

    # 사용량 확인
    now = datetime.utcnow()
    usage = await usage_service.get_current_usage(test_user.id, now.year, now.month)

    assert usage is not None
    assert usage.papers_analyzed == 1
    assert usage.rag_queries == 0


@pytest.mark.asyncio
async def test_usage_limit_exceeded(db_session: AsyncSession, test_user: User, test_plan_limits):
    """사용량 한도 초과 테스트"""
    usage_service = UsageService(db_session)

    # Free 플랜은 papers_per_month=10
    # 10번까지는 성공
    for i in range(10):
        await usage_service.check_and_increment(test_user.id, "papers_analyzed", "free")

    # 11번째는 실패해야 함
    with pytest.raises(UsageLimitExceeded) as exc_info:
        await usage_service.check_and_increment(test_user.id, "papers_analyzed", "free")

    assert "월별 사용량 한도를 초과" in str(exc_info.value.message)
    assert exc_info.value.status_code == 429
    assert exc_info.value.details["upgrade_required"] is True


@pytest.mark.asyncio
async def test_usage_unlimited_plan(db_session: AsyncSession, test_user: User, test_plan_limits):
    """무제한 플랜 테스트"""
    usage_service = UsageService(db_session)

    # Pro 플랜은 papers_per_month=-1 (unlimited)
    # 100번 실행해도 에러 없어야 함
    for i in range(100):
        await usage_service.check_and_increment(test_user.id, "papers_analyzed", "pro")

    # 사용량 확인
    now = datetime.utcnow()
    usage = await usage_service.get_current_usage(test_user.id, now.year, now.month)

    assert usage.papers_analyzed == 100


@pytest.mark.asyncio
async def test_get_plan_limits(client: AsyncClient, test_plan_limits, auth_headers):
    """플랜 제한 조회 테스트"""
    response = await client.get(
        "/api/v1/usage/limits/free",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["plan_name"] == "free"
    assert data["papers_per_month"] == 10
    assert data["rag_queries_per_month"] == 50
    assert data["pdf_export"] is False


@pytest.mark.asyncio
async def test_usage_history(
    client: AsyncClient, db_session: AsyncSession, test_user: User, test_plan_limits, auth_headers
):
    """사용량 히스토리 조회 테스트"""
    usage_service = UsageService(db_session)

    # 사용량 생성
    for i in range(5):
        await usage_service.check_and_increment(test_user.id, "papers_analyzed", "free")
        await usage_service.check_and_increment(test_user.id, "rag_queries", "free")

    # 히스토리 조회
    response = await client.get(
        "/api/v1/usage/history?months=3",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["papers_analyzed"] == 5
    assert data[0]["rag_queries"] == 5


@pytest.mark.asyncio
async def test_check_feature_access_pdf_export(
    db_session: AsyncSession, test_user: User, test_plan_limits
):
    """기능 접근 권한 체크 테스트 (PDF Export)"""
    usage_service = UsageService(db_session)

    # Free 플랜은 PDF export 불가
    has_access = await usage_service.check_feature_access(test_user.id, "pdf_export", "free")
    assert has_access is False

    # Basic 플랜은 PDF export 가능
    has_access = await usage_service.check_feature_access(test_user.id, "pdf_export", "basic")
    assert has_access is True
