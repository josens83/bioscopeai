"""
Redis 캐싱 서비스
"""
import json
import hashlib
from typing import Optional, Any
from redis import asyncio as aioredis
from app.core.config import settings
from app.core.logging import app_logger as logger


class RedisCache:
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
        # 인자들을 문자열로 변환하여 해시 생성
        key_parts = [prefix] + [str(arg) for arg in args]
        key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
        key_string = ":".join(key_parts)

        # 긴 키는 해시로 변환
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

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600  # 기본 1시간
    ) -> bool:
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

    # 특정 도메인별 캐싱 메서드

    async def get_pubmed_search(self, query: str, max_results: int) -> Optional[list]:
        """PubMed 검색 결과 캐시 조회"""
        key = self._generate_key("pubmed", query=query, max=max_results)
        return await self.get(key)

    async def set_pubmed_search(
        self,
        query: str,
        max_results: int,
        results: list,
        expire: int = 3600  # 1시간
    ) -> bool:
        """PubMed 검색 결과 캐시 저장"""
        key = self._generate_key("pubmed", query=query, max=max_results)
        return await self.set(key, results, expire)

    async def get_rag_answer(
        self,
        question: str,
        paper_id: Optional[int] = None
    ) -> Optional[dict]:
        """RAG Q&A 결과 캐시 조회"""
        key = self._generate_key("rag_qa", question=question, paper_id=paper_id)
        return await self.get(key)

    async def set_rag_answer(
        self,
        question: str,
        answer: dict,
        paper_id: Optional[int] = None,
        expire: int = 7200  # 2시간
    ) -> bool:
        """RAG Q&A 결과 캐시 저장"""
        key = self._generate_key("rag_qa", question=question, paper_id=paper_id)
        return await self.set(key, answer, expire)

    async def get_paper_summary(self, paper_id: int) -> Optional[dict]:
        """논문 요약 캐시 조회"""
        key = self._generate_key("summary", paper_id=paper_id)
        return await self.get(key)

    async def set_paper_summary(
        self,
        paper_id: int,
        summary: dict,
        expire: int = 86400  # 24시간
    ) -> bool:
        """논문 요약 캐시 저장"""
        key = self._generate_key("summary", paper_id=paper_id)
        return await self.set(key, summary, expire)

    async def invalidate_paper_cache(self, paper_id: int):
        """특정 논문 관련 캐시 무효화"""
        await self.delete_pattern(f"*paper_id={paper_id}*")
        await self.delete_pattern(f"summary:paper_id={paper_id}")


# 싱글톤 인스턴스
cache = RedisCache()


async def get_cache() -> RedisCache:
    """캐시 인스턴스 가져오기"""
    return cache
