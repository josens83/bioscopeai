"""
Rate Limiting 설정 및 미들웨어

API 요청 제한을 통해 남용 방지 및 시스템 보호
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.constants.api import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_HOUR
from app.core.logging import app_logger as logger
from typing import Callable
import time


# Limiter 인스턴스 생성
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{RATE_LIMIT_PER_MINUTE}/minute",
        f"{RATE_LIMIT_PER_HOUR}/hour"
    ],
    storage_uri="memory://",  # 프로덕션에서는 Redis 사용 권장
    strategy="fixed-window"
)


# 사용자별 Rate Limit (인증된 사용자)
def get_user_id_from_request(request: Request) -> str:
    """
    요청에서 사용자 ID 추출 (rate limiting용)

    인증된 사용자는 user_id 기반, 그 외는 IP 기반
    """
    # JWT 토큰에서 사용자 ID 추출 (이미 인증된 경우)
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    # API 키 사용자
    if hasattr(request.state, "api_key_user") and request.state.api_key_user:
        return f"api_key:{request.state.api_key_user.id}"

    # 인증되지 않은 경우 IP 주소 사용
    return f"ip:{get_remote_address(request)}"


# 플랜별 Rate Limit
PLAN_RATE_LIMITS = {
    "free": {
        "minute": 10,
        "hour": 100,
        "day": 500,
    },
    "basic": {
        "minute": 30,
        "hour": 500,
        "day": 5000,
    },
    "premium": {
        "minute": 100,
        "hour": 2000,
        "day": 20000,
    },
    "enterprise": {
        "minute": 1000,
        "hour": 10000,
        "day": 100000,
    },
}


def get_rate_limit_for_user(request: Request) -> str:
    """
    사용자 플랜에 따른 Rate Limit 반환

    Returns:
        "60/minute" 형식의 문자열
    """
    # 사용자 구독 플랜 확인
    if hasattr(request.state, "user") and request.state.user:
        user = request.state.user

        # 사용자의 구독 플랜 가져오기
        if hasattr(user, "subscription") and user.subscription:
            tier = user.subscription.tier
            limits = PLAN_RATE_LIMITS.get(tier, PLAN_RATE_LIMITS["free"])
        else:
            limits = PLAN_RATE_LIMITS["free"]

        return f"{limits['minute']}/minute;{limits['hour']}/hour"

    # 기본 Rate Limit (인증되지 않은 사용자)
    return f"{RATE_LIMIT_PER_MINUTE}/minute;{RATE_LIMIT_PER_HOUR}/hour"


# Rate Limit 에러 핸들러
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Rate Limit 초과 시 에러 응답

    HTTP 429 Too Many Requests
    """
    # Retry-After 헤더 계산
    retry_after = int(exc.detail.split()[-1].rstrip('s'))

    logger.warning(
        f"Rate limit exceeded: {get_remote_address(request)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "retry_after": retry_after
        }
    )

    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RateLimitExceeded",
                "message": "요청 횟수 제한을 초과했습니다. 잠시 후 다시 시도해주세요.",
                "details": {
                    "retry_after": retry_after,
                    "limit_info": str(exc.detail)
                }
            },
            "timestamp": time.time()
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": request.headers.get("X-RateLimit-Limit", ""),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + retry_after)
        }
    )


# Rate Limit 데코레이터 (다양한 제한)
class RateLimits:
    """Rate Limit 프리셋"""

    # 인증 관련 (더 엄격)
    AUTH = "5/minute"  # 로그인, 회원가입
    PASSWORD_RESET = "3/hour"  # 비밀번호 재설정

    # API 호출
    API_READ = "100/minute"  # 읽기 작업
    API_WRITE = "30/minute"  # 쓰기 작업
    API_HEAVY = "10/minute"  # 무거운 작업 (분석 등)

    # 파일 업로드
    FILE_UPLOAD = "10/minute"  # 파일 업로드

    # 검색
    SEARCH = "30/minute"  # 검색 요청


# Rate Limit 미들웨어
class RateLimitMiddleware:
    """
    Rate Limit 미들웨어

    모든 요청에 Rate Limit 헤더 추가
    """

    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Rate Limit 정보를 응답 헤더에 추가
        response = await call_next(request)

        # Rate Limit 헤더 추가 (선택사항)
        if hasattr(request.state, "view_rate_limit"):
            response.headers["X-RateLimit-Limit"] = str(request.state.view_rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(
                getattr(request.state, "view_rate_limit_remaining", 0)
            )
            response.headers["X-RateLimit-Reset"] = str(
                getattr(request.state, "view_rate_limit_reset", 0)
            )

        return response


# Redis 기반 Rate Limiting (프로덕션용)
async def init_redis_limiter(redis_url: str):
    """
    Redis 기반 Rate Limiter 초기화

    프로덕션 환경에서 사용
    """
    global limiter

    limiter = Limiter(
        key_func=get_user_id_from_request,
        default_limits=[
            f"{RATE_LIMIT_PER_MINUTE}/minute",
            f"{RATE_LIMIT_PER_HOUR}/hour"
        ],
        storage_uri=redis_url,
        strategy="fixed-window"
    )

    logger.info(f"Redis-based rate limiter initialized: {redis_url}")
