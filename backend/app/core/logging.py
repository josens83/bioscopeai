"""
구조화된 로깅 시스템 (Loguru)
"""
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging():
    """로깅 시스템 초기화"""

    # 기본 핸들러 제거
    logger.remove()

    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 콘솔 로깅 (개발 환경)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.ENVIRONMENT == "development" else "INFO",
        colorize=True,
    )

    # 일반 로그 파일 (INFO 이상)
    logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="100 MB",  # 100MB마다 로테이션
        retention="30 days",  # 30일간 보관
        compression="zip",  # 압축 저장
        encoding="utf-8",
    )

    # 에러 로그 파일 (ERROR 이상)
    logger.add(
        log_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="50 MB",
        retention="90 days",  # 에러는 90일간 보관
        compression="zip",
        encoding="utf-8",
        backtrace=True,  # 전체 스택 트레이스
        diagnose=True,  # 변수 값 포함
    )

    # JSON 형식 로그 (프로덕션 환경)
    if settings.ENVIRONMENT == "production":
        logger.add(
            log_dir / "app.json",
            format="{message}",
            level="INFO",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            serialize=True,  # JSON 직렬화
        )

    logger.info("로깅 시스템 초기화 완료")
    return logger


# 싱글톤 로거
app_logger = setup_logging()
