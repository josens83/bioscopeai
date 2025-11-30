"""
Auth Domain Dependencies
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from .models import User
from .exceptions import InvalidTokenException, UserNotFoundException, InactiveUserException

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
    """현재 사용자 가져오기 (JWT 토큰 기반)"""
    token = credentials.credentials

    # 토큰 검증
    payload = verify_token(token)
    if not payload:
        raise InvalidTokenException()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    # 사용자 조회
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise UserNotFoundException()

    if not user.is_active:
        raise InactiveUserException()

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """활성 사용자 확인"""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """슈퍼유저 권한 확인"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="슈퍼유저 권한이 필요합니다"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """관리자 권한 확인 (role 기반)"""
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user
