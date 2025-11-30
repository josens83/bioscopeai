"""
API 키 관리 서비스

API 키 생성, 검증, 해시 등의 기능 제공
"""
import secrets
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.api_key import APIKey
from app.models.user import User
from datetime import datetime, timedelta
from typing import Optional, List
import json


class APIKeyService:
    """API 키 관리 서비스"""

    @staticmethod
    def generate_api_key() -> tuple[str, str, str]:
        """
        새로운 API 키 생성

        Returns:
            (raw_key, hashed_key, prefix): 원본 키, 해시된 키, 프리픽스
        """
        # 프리픽스 (bsa = BioScopeAI)
        prefix = "bsa"

        # 랜덤 키 생성 (32바이트 = 64 hex 문자)
        random_part = secrets.token_hex(32)

        # 전체 키: prefix_randompart
        raw_key = f"{prefix}_{random_part}"

        # 해시 (저장용)
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

        # 표시용 프리픽스 (처음 12자)
        display_prefix = raw_key[:12] + "..."

        return raw_key, hashed_key, display_prefix

    @staticmethod
    async def create_api_key(
        db: AsyncSession,
        user: User,
        name: str,
        description: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        rate_limit: Optional[int] = None,
        expires_days: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None,
    ) -> tuple[APIKey, str]:
        """
        사용자를 위한 새 API 키 생성

        Args:
            db: 데이터베이스 세션
            user: 키를 소유할 사용자
            name: 키 이름
            description: 키 설명
            scopes: 권한 범위 리스트
            rate_limit: 분당 요청 제한
            expires_days: 만료까지 일수 (None=무제한)
            ip_whitelist: 허용 IP 리스트

        Returns:
            (APIKey 객체, 원본 API 키 문자열)
        """
        raw_key, hashed_key, display_prefix = APIKeyService.generate_api_key()

        # 만료 날짜 계산
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)

        # API 키 객체 생성
        api_key = APIKey(
            user_id=user.id,
            name=name,
            key=hashed_key,
            prefix=display_prefix,
            description=description,
            scopes=json.dumps(scopes) if scopes else None,
            rate_limit=rate_limit,
            expires_at=expires_at,
            ip_whitelist=json.dumps(ip_whitelist) if ip_whitelist else None,
        )

        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)

        return api_key, raw_key

    @staticmethod
    async def verify_api_key(
        db: AsyncSession,
        raw_key: str,
        required_scope: Optional[str] = None,
    ) -> Optional[User]:
        """
        API 키 검증 및 사용자 반환

        Args:
            db: 데이터베이스 세션
            raw_key: 원본 API 키 문자열
            required_scope: 필요한 권한 (예: "papers:read")

        Returns:
            User 객체 (유효한 경우) 또는 None
        """
        # 키 해시
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

        # 데이터베이스에서 조회
        result = await db.execute(
            select(APIKey).where(APIKey.key == hashed_key, APIKey.is_active == True)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return None

        # 만료 확인
        if api_key.is_expired:
            return None

        # 권한 확인
        if required_scope and api_key.scopes:
            scopes = json.loads(api_key.scopes)
            if required_scope not in scopes and "*" not in scopes:
                return None

        # 사용 기록 업데이트
        api_key.last_used_at = datetime.utcnow()
        api_key.usage_count += 1
        await db.commit()

        # 사용자 조회
        result = await db.execute(
            select(User).where(User.id == api_key.user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()

        return user

    @staticmethod
    async def get_user_api_keys(db: AsyncSession, user_id: int) -> List[APIKey]:
        """사용자의 모든 API 키 조회"""
        result = await db.execute(
            select(APIKey).where(APIKey.user_id == user_id).order_by(APIKey.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def revoke_api_key(db: AsyncSession, api_key_id: int, user_id: int) -> bool:
        """API 키 비활성화 (취소)"""
        result = await db.execute(
            select(APIKey).where(APIKey.id == api_key_id, APIKey.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        api_key.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def delete_api_key(db: AsyncSession, api_key_id: int, user_id: int) -> bool:
        """API 키 완전 삭제"""
        result = await db.execute(
            select(APIKey).where(APIKey.id == api_key_id, APIKey.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        await db.delete(api_key)
        await db.commit()
        return True
