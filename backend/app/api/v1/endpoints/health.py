"""
Health Check 엔드포인트
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.cache_service import cache
from app.core.config import settings
from datetime import datetime
import psutil
import sys

router = APIRouter()


@router.get("/health")
async def basic_health_check():
    """기본 헬스 체크 (빠른 응답)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """상세 헬스 체크 (DB, Redis, 시스템 상태 포함)"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }

    # 데이터베이스 체크
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "type": "postgresql",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # Redis 체크
    try:
        if cache.redis:
            await cache.redis.ping()
            # Redis 정보 가져오기
            info = await cache.redis.info()
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", "N/A"),
            }
        else:
            health_status["checks"]["redis"] = {
                "status": "disconnected",
                "message": "Redis not connected",
            }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # 시스템 리소스 체크
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available // (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free // (1024 * 1024 * 1024),
        }

        # 리소스 임계값 체크
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["checks"]["system"]["warning"] = "High resource usage"

    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "unknown",
            "error": str(e),
        }

    # Python 버전
    health_status["python_version"] = sys.version.split()[0]

    return health_status


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """준비 상태 체크 (Kubernetes readiness probe용)"""
    try:
        # DB 연결 확인
        await db.execute(text("SELECT 1"))

        # Redis 연결 확인
        if cache.redis:
            await cache.redis.ping()

        return {"status": "ready"}
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e)
        }


@router.get("/health/live")
async def liveness_check():
    """생존 상태 체크 (Kubernetes liveness probe용)"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
