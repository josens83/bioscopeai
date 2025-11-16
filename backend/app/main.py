from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import app_logger as logger
from app.core.middleware import RequestLoggingMiddleware
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 및 종료 시 실행되는 로직"""
    # 시작 시
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작 중...")
    logger.info(f"환경: {settings.ENVIRONMENT}")
    await init_db()
    logger.success("✅ 애플리케이션 초기화 완료")
    yield
    # 종료 시
    logger.info("⏹️  애플리케이션 종료 중...")
    logger.success("✅ 정상 종료됨")


# Rate Limiter 초기화
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate Limit 상태 및 핸들러 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 로깅 미들웨어
app.add_middleware(RequestLoggingMiddleware)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """루트 엔드포인트"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """헬스 체크 (Rate limit 없음)"""
    return {"status": "healthy"}
