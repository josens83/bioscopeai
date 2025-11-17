from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import app_logger as logger
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.core.error_handlers import register_exception_handlers
from app.core.config_validator import validate_environment_on_startup
from app.services.cache_service import cache
from app.api.v1.router import api_router
import sentry_sdk


# 환경 설정 검증 (앱 시작 전)
validate_environment_on_startup()

# Sentry 초기화 (DSN이 설정된 경우에만)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
        # 성능 모니터링
        enable_tracing=True,
        # FastAPI 통합
        integrations=[],
        # 민감한 데이터 필터링
        before_send=lambda event, hint: event if settings.ENVIRONMENT != "development" else event,
    )
    logger.info("✅ Sentry 초기화 완료")
else:
    logger.info("ℹ️  Sentry DSN이 설정되지 않음 - 에러 추적 비활성화")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 및 종료 시 실행되는 로직"""
    # 시작 시
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작 중...")
    logger.info(f"환경: {settings.ENVIRONMENT}")

    # 데이터베이스 초기화
    await init_db()

    # Redis 연결
    await cache.connect()

    logger.success("✅ 애플리케이션 초기화 완료")
    yield

    # 종료 시
    logger.info("⏹️  애플리케이션 종료 중...")
    await cache.disconnect()
    logger.success("✅ 정상 종료됨")


# Rate Limiter 초기화
limiter = Limiter(key_func=get_remote_address)

# API 메타데이터
description = """
🧬 **BioscopeAI** - AI 기반 생물의학 논문 분석 플랫폼

## 주요 기능

### 📄 논문 관리
* PubMed 논문 검색 및 저장
* PDF 업로드 및 텍스트 추출
* 논문 메타데이터 관리

### 🤖 AI 분석
* **RAG 기반 질문-답변**: 논문 내용에 대한 자연어 질문
* **논문 요약**: AI가 자동으로 핵심 내용 요약
* **논문 비교**: 여러 논문의 유사점과 차이점 분석

### 💳 구독 관리
* Free, Basic, Premium, Enterprise 플랜
* Stripe 결제 통합
* 사용량 추적

## 인증

대부분의 엔드포인트는 JWT 토큰 인증이 필요합니다:

1. `/api/v1/auth/register` 또는 `/api/v1/auth/login`으로 토큰 획득
2. `Authorization: Bearer <access_token>` 헤더에 포함하여 요청

## 데모 계정

```
이메일: demo@bioscopeai.com
비밀번호: demo1234
```

## Rate Limiting

* 일반 API: 10 req/min
* 인증 API: 5-10 req/min
* PubMed 검색: API 제한 적용

## 문서

* **Swagger UI**: `/docs`
* **ReDoc**: `/redoc`
* **전체 문서**: [GitHub](https://github.com/josens83/bioscopeai)
"""

tags_metadata = [
    {
        "name": "health",
        "description": "시스템 상태 확인 (Health Check, Readiness, Liveness)",
    },
    {
        "name": "auth",
        "description": "사용자 인증 및 등록 (회원가입, 로그인, 비밀번호 재설정, 이메일 인증)",
    },
    {
        "name": "papers",
        "description": "논문 관리 (PubMed 검색, PDF 업로드, CRUD)",
    },
    {
        "name": "analysis",
        "description": "AI 기반 논문 분석 (Q&A, 요약, 비교) - 사용량 추적 적용",
    },
    {
        "name": "usage",
        "description": "사용량 조회 및 플랜 정보 (내 사용량, 플랜 비교, 기능 접근 권한)",
    },
    {
        "name": "subscription",
        "description": "구독 플랜 및 결제 관리 (Stripe 통합, 웹훅 처리)",
    },
    {
        "name": "admin",
        "description": "관리자 전용 (사용자 통계, 비즈니스 메트릭, 사용량 분석)",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "BioscopeAI Team",
        "url": "https://github.com/josens83/bioscopeai",
        "email": "support@bioscopeai.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# 전역 예외 핸들러 등록
register_exception_handlers(app)

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

# 보안 헤더 미들웨어
app.add_middleware(SecurityHeadersMiddleware)

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
        "health": "/api/v1/health",
    }
