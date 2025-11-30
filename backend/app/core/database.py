from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from .config import settings
from app.core.logging import app_logger as logger

# 비동기 엔진 생성
# 프로덕션 환경을 위한 최적화된 connection pool 설정
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,  # 기본 연결 수
    max_overflow=settings.DATABASE_MAX_OVERFLOW,  # 추가 가능한 최대 연결 수
    pool_timeout=30,  # 연결 대기 시간 (초)
    pool_recycle=3600,  # 1시간마다 연결 재활용 (MySQL 8시간 timeout 방지)
    pool_pre_ping=True,  # 연결 사용 전 health check (끊긴 연결 감지)
    echo_pool=settings.DEBUG,  # 디버그 모드에서 pool 로깅
    connect_args={
        "server_settings": {"application_name": "bioscopeai"},
    } if "postgresql" in settings.DATABASE_URL else {},
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 베이스 모델
Base = declarative_base()


async def get_db() -> AsyncSession:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """데이터베이스 초기화"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
