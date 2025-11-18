"""
Cache Service - Redis 기반 캐싱
"""
import json
import hashlib
from typing import Optional, Any
from redis import asyncio as aioredis
from app.core.config import settings
from app.core.logging import app_logger as logger


class CacheService:
    """Redis 기반 캐싱 서비스"""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Redis 연결"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis.ping()
            logger.info("✅ Redis 연결 성공")
        except Exception as e:
            logger.error(f"❌ Redis 연결 실패: {e}")
            self.redis = None

    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis 연결 종료")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
        key_string = ":".join(key_parts)

        if len(key_string) > 200:
            hash_suffix = hashlib.md5(key_string.encode()).hexdigest()[:16]
            key_string = f"{prefix}:{hash_suffix}"

        return key_string

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        if not self.redis:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"🎯 캐시 HIT: {key}")
                return json.loads(value)
            else:
                logger.debug(f"❌ 캐시 MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"캐시 조회 실패: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """캐시에 값 저장"""
        if not self.redis:
            return False

        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(value, default=str)
            )
            logger.debug(f"💾 캐시 저장: {key} (TTL: {expire}s)")
            return True
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """캐시 삭제"""
        if not self.redis:
            return False

        try:
            await self.redis.delete(key)
            logger.debug(f"🗑️  캐시 삭제: {key}")
            return True
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """패턴에 맞는 모든 캐시 삭제"""
        if not self.redis:
            return 0

        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"🗑️  캐시 {deleted}개 삭제: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"캐시 패턴 삭제 실패: {e}")
            return 0


# 싱글톤 인스턴스
cache = CacheService()
