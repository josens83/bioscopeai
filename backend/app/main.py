from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import app_logger as logger
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.core.error_handlers import register_exception_handlers
from app.core.config_validator import validate_environment_on_startup
from app.core.sentry import init_sentry
from app.core.rate_limiting import limiter, rate_limit_exceeded_handler, RateLimitMiddleware
from app.services.cache_service import cache
from app.api.v1.router import api_router


# 환경 설정 검증 (앱 시작 전)
validate_environment_on_startup()

# Sentry 초기화 (프로덕션 에러 모니터링)
init_sentry()


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

    # Redis 기반 Rate Limiter 초기화 (프로덕션)
    if settings.ENVIRONMENT == "production" and settings.REDIS_URL:
        from app.core.rate_limiting import init_redis_limiter
        await init_redis_limiter(settings.REDIS_URL)
        logger.info("✅ Redis 기반 Rate Limiter 초기화 완료")

    logger.success("✅ 애플리케이션 초기화 완료")
    yield

    # 종료 시
    logger.info("⏹️  애플리케이션 종료 중...")
    await cache.disconnect()
    logger.success("✅ 정상 종료됨")

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
        "externalDocs": {
            "description": "Health Check 가이드",
            "url": "https://github.com/josens83/bioscopeai#health-check",
        },
    },
    {
        "name": "auth",
        "description": "사용자 인증 및 등록 (회원가입, 로그인, 비밀번호 재설정, 이메일 인증)",
    },
    {
        "name": "users",
        "description": "사용자 프로필 관리 (정보 조회, 수정, 비밀번호 변경)",
    },
    {
        "name": "api-keys",
        "description": "API 키 관리 (개발자용 API 접근 키 생성, 관리)",
    },
    {
        "name": "terms",
        "description": "서비스 이용약관 동의 관리",
    },
    {
        "name": "promotions",
        "description": "프로모션 코드 및 할인 관리",
    },
    {
        "name": "2fa",
        "description": "2단계 인증 설정 (TOTP 기반 보안 강화)",
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
    servers=[
        {"url": "http://localhost:8000", "description": "로컬 개발 서버"},
        {"url": "https://staging.bioscopeai.com", "description": "스테이징 서버"},
        {"url": "https://api.bioscopeai.com", "description": "프로덕션 서버"},
    ],
)


# OpenAPI 스키마 커스터마이징 (JWT 인증 추가)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()

    # Security Schemes 추가
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT 액세스 토큰을 입력하세요. `/api/v1/auth/login`에서 토큰을 획득할 수 있습니다.",
        },
        "APIKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API 키를 입력하세요. 개발자 설정에서 API 키를 생성할 수 있습니다.",
        },
    }

    # 전역 보안 요구사항 (기본값)
    openapi_schema["security"] = [{"BearerAuth": []}]

    # 에러 응답 스키마 추가
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "error": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "에러 메시지"},
                    "code": {"type": "string", "description": "에러 코드"},
                    "details": {"type": "object", "description": "추가 상세 정보"},
                },
                "required": ["message", "code"],
            }
        },
        "example": {
            "error": {
                "message": "인증이 필요합니다.",
                "code": "Unauthorized",
                "details": None,
            }
        },
    }

    openapi_schema["components"]["schemas"]["ValidationErrorResponse"] = {
        "type": "object",
        "properties": {
            "error": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "code": {"type": "string"},
                    "details": {
                        "type": "object",
                        "properties": {
                            "validation_errors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "field": {"type": "string"},
                                        "message": {"type": "string"},
                                        "type": {"type": "string"},
                                    },
                                },
                            }
                        },
                    },
                },
            }
        },
        "example": {
            "error": {
                "message": "입력값 검증에 실패했습니다.",
                "code": "ValidationError",
                "details": {
                    "validation_errors": [
                        {
                            "field": "body.email",
                            "message": "value is not a valid email address",
                            "type": "value_error.email",
                        }
                    ]
                },
            }
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# 전역 예외 핸들러 등록
register_exception_handlers(app)

# Rate Limit 상태 및 핸들러 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limit 헤더 미들웨어
app.add_middleware(RateLimitMiddleware)

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
