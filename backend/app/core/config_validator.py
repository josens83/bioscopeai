"""
환경 설정 검증 및 초기화
"""
from app.core.config import settings
from app.core.logging import app_logger as logger
from pathlib import Path
import sys


class ConfigValidator:
    """환경 설정 검증"""

    @staticmethod
    def validate_required_settings() -> bool:
        """필수 설정값 검증"""
        errors = []
        warnings = []

        # 필수 환경변수 (프로덕션)
        if settings.ENVIRONMENT == "production":
            if settings.DEBUG:
                errors.append("⚠️  프로덕션 환경에서 DEBUG=True는 보안 위험입니다")

            if settings.SECRET_KEY == "your-secret-key-here-change-in-production":
                errors.append("🔐 SECRET_KEY를 프로덕션용으로 변경해주세요")

            if not settings.SENTRY_DSN:
                warnings.append("⚠️  Sentry DSN이 설정되지 않았습니다 (에러 추적 비활성화)")

        # 데이터베이스
        if not settings.DATABASE_URL:
            errors.append("❌ DATABASE_URL이 설정되지 않았습니다")
        elif "localhost" in settings.DATABASE_URL and settings.ENVIRONMENT == "production":
            warnings.append("⚠️  프로덕션 환경에서 localhost DB를 사용하고 있습니다")

        # JWT
        if not settings.JWT_SECRET_KEY:
            errors.append("❌ JWT_SECRET_KEY가 설정되지 않았습니다")
        elif settings.JWT_SECRET_KEY == "your-jwt-secret-key-here":
            errors.append("🔐 JWT_SECRET_KEY를 변경해주세요")

        # OpenAI
        if not settings.OPENAI_API_KEY:
            errors.append("❌ OPENAI_API_KEY가 설정되지 않았습니다")
        elif settings.OPENAI_API_KEY.startswith("sk-your-"):
            errors.append("🔑 OPENAI_API_KEY를 실제 키로 변경해주세요")

        # Stripe
        if not settings.STRIPE_SECRET_KEY:
            errors.append("❌ STRIPE_SECRET_KEY가 설정되지 않았습니다")
        elif settings.STRIPE_SECRET_KEY.startswith("sk_test") and settings.ENVIRONMENT == "production":
            warnings.append("⚠️  프로덕션 환경에서 Stripe 테스트 키를 사용하고 있습니다")

        # SMTP (이메일)
        if settings.ENVIRONMENT == "production":
            if not hasattr(settings, 'SMTP_USER') or not settings.SMTP_USER:
                warnings.append("⚠️  SMTP_USER가 설정되지 않았습니다 (이메일 발송 불가)")

        # 디렉토리 생성
        upload_dir = Path(settings.UPLOAD_DIR)
        if not upload_dir.exists():
            try:
                upload_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ 업로드 디렉토리 생성: {settings.UPLOAD_DIR}")
            except Exception as e:
                errors.append(f"❌ 업로드 디렉토리 생성 실패: {e}")

        vector_dir = Path(settings.VECTOR_DB_PATH).parent
        if not vector_dir.exists():
            try:
                vector_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ 벡터 DB 디렉토리 생성: {vector_dir}")
            except Exception as e:
                errors.append(f"❌ 벡터 DB 디렉토리 생성 실패: {e}")

        # 결과 출력
        if errors:
            logger.error("❌ 설정 검증 실패:")
            for error in errors:
                logger.error(f"  {error}")
            return False

        if warnings:
            logger.warning("⚠️  경고:")
            for warning in warnings:
                logger.warning(f"  {warning}")

        logger.success("✅ 환경 설정 검증 완료")
        return True

    @staticmethod
    def print_config_summary():
        """설정 요약 출력"""
        logger.info("=" * 60)
        logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info("=" * 60)
        logger.info(f"환경: {settings.ENVIRONMENT}")
        logger.info(f"디버그: {settings.DEBUG}")
        logger.info(f"데이터베이스: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'N/A'}")
        logger.info(f"Redis: {settings.REDIS_URL}")
        logger.info(f"Sentry: {'활성화' if settings.SENTRY_DSN else '비활성화'}")
        logger.info(f"CORS 허용: {', '.join(settings.CORS_ORIGINS[:3])}")
        logger.info("=" * 60)


def validate_environment_on_startup():
    """시작 시 환경 검증"""
    ConfigValidator.print_config_summary()

    if not ConfigValidator.validate_required_settings():
        logger.error("❌ 환경 설정 검증 실패 - 애플리케이션을 시작할 수 없습니다")
        logger.error("💡 .env 파일을 확인하고 필수 설정을 완료해주세요")
        sys.exit(1)
