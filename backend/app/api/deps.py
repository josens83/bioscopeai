from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.models.user import User
from app.services.api_key_service import APIKeyService

security = HTTPBearer()


async def get_db() -> Generator:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """현재 사용자 가져오기"""
    token = credentials.credentials

    # 토큰 검증
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보입니다",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
        )

    # 사용자 조회
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """활성 사용자 확인"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다",
        )
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """관리자 권한 확인"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return current_user


async def get_user_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    API 키로 사용자 인증

    헤더: X-API-Key: bsa_xxxxx...
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API 키가 필요합니다",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    user = await APIKeyService.verify_api_key(db, x_api_key)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 API 키입니다",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return user


async def get_user_from_token_or_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    JWT 토큰 또는 API 키로 사용자 인증

    우선순위: API 키 > JWT 토큰
    """
    # API 키 우선 확인
    if x_api_key:
        user = await APIKeyService.verify_api_key(db, x_api_key)
        if user:
            return user

    # JWT 토큰 확인
    if credentials:
        token = credentials.credentials
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                result = await db.execute(select(User).where(User.id == int(user_id)))
                user = result.scalar_one_or_none()
                if user and user.is_active:
                    return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효한 인증 정보가 필요합니다 (Bearer Token 또는 X-API-Key)",
        headers={"WWW-Authenticate": "Bearer, ApiKey"},
    )
