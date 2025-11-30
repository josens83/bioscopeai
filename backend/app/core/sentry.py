"""
Sentry 에러 모니터링 설정

프로덕션 환경에서 에러 추적, 성능 모니터링, 사용자 피드백 수집
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from app.core.config import settings
from app.core.logging import app_logger as logger


def init_sentry():
    """
    Sentry 초기화

    - 에러 추적
    - 성능 모니터링 (APM)
    - 릴리스 추적
    - 환경별 설정
    """
    # Sentry가 비활성화되어 있거나 DSN이 없으면 건너뛰기
    if not settings.SENTRY_DSN or settings.ENVIRONMENT == "development":
        logger.info("Sentry disabled (development mode or no DSN)")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # 환경 설정
        environment=settings.ENVIRONMENT,
        release=f"bioscopeai@{settings.APP_VERSION}",

        # FastAPI 통합
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",  # endpoint 이름으로 트랜잭션 그룹화
            ),
            SqlalchemyIntegration(),  # SQL 쿼리 추적
            RedisIntegration(),  # Redis 작업 추적
            LoggingIntegration(
                level=None,  # 로그 레벨 캡처 (기본값 사용)
                event_level=None,  # 이벤트로 전송할 로그 레벨 (기본값 사용)
            ),
        ],

        # 샘플링 비율 (성능 모니터링)
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,

        # 프로파일링 샘플 비율
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,

        # PII(개인정보) 전송 여부
        send_default_pii=False,  # 보안상 False

        # 요청 본문 크기 제한
        max_request_body_size="medium",  # small, medium, large, always, never

        # 에러 전송 전 필터링
        before_send=before_send,

        # 브레드크럼 설정 (디버깅 정보)
        max_breadcrumbs=50,

        # 첨부 파일 크기 제한
        max_value_length=2048,
    )

    logger.info(f"Sentry initialized: environment={settings.ENVIRONMENT}, release=bioscopeai@{settings.APP_VERSION}")


def before_send(event, hint):
    """
    에러 전송 전 처리

    - 민감한 정보 제거
    - 특정 에러 필터링
    - 추가 컨텍스트 정보 추가
    """
    # HTTP 401, 403, 404는 Sentry로 보내지 않음 (일반적인 에러)
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if exc_type.__name__ in ["HTTPException"]:
            # HTTPException의 status_code 확인
            if hasattr(exc_value, "status_code"):
                status_code = exc_value.status_code
                if status_code in [401, 403, 404]:
                    # 이런 에러는 Sentry로 보내지 않음
                    return None

    # 민감한 정보가 포함된 헤더 제거
    if "request" in event:
        headers = event["request"].get("headers", {})
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"

    # 비밀번호 등 민감한 데이터 필터링
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            sensitive_fields = ["password", "new_password", "current_password", "token", "secret"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[Filtered]"

    return event


def capture_exception(error: Exception, context: dict = None):
    """
    예외를 Sentry로 전송

    Args:
        error: 발생한 예외
        context: 추가 컨텍스트 정보
    """
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "development":
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """
    메시지를 Sentry로 전송

    Args:
        message: 전송할 메시지
        level: 로그 레벨 (debug, info, warning, error, fatal)
        context: 추가 컨텍스트 정보
    """
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "development":
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: int = None, email: str = None, username: str = None):
    """
    사용자 컨텍스트 설정

    에러 발생 시 어떤 사용자에게 문제가 있었는지 추적
    """
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "development":
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username,
        })


def clear_user_context():
    """사용자 컨텍스트 제거"""
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "development":
        sentry_sdk.set_user(None)
