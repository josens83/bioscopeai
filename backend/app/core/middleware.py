"""
커스텀 미들웨어
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import app_logger as logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        # 시작 시간
        start_time = time.time()

        # 요청 정보 로깅
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        # 응답 처리
        try:
            response = await call_next(request)

            # 처리 시간 계산
            process_time = time.time() - start_time

            # 응답 로깅
            logger.info(
                f"← {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                },
            )

            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 에러 로깅
            process_time = time.time() - start_time
            logger.error(
                f"✗ {request.method} {request.url.path} - ERROR ({process_time:.3f}s)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                },
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    보안 헤더 미들웨어

    OWASP 권장 보안 헤더 추가
    https://owasp.org/www-project-secure-headers/
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # X-Content-Type-Options: MIME 타입 스니핑 방지
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection: XSS 공격 탐지 및 차단 (구형 브라우저용)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # X-Frame-Options: Clickjacking 공격 방지
        response.headers["X-Frame-Options"] = "DENY"

        # Content-Security-Policy: XSS 및 데이터 인젝션 공격 방지
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src https://js.stripe.com https://hooks.stripe.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

        # Strict-Transport-Security: HTTPS 강제 (프로덕션 환경만)
        from app.core.config import settings
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Referrer-Policy: 리퍼러 정보 제어
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: 브라우저 기능 접근 제어
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=(), "
            "fullscreen=(self)"
        )

        # 서버 정보 숨기기
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)

        return response
