"""
비밀번호 재설정 서비스

안전한 비밀번호 재설정 워크플로우
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import secrets
from datetime import datetime, timedelta

from app.models.user import User
from app.services.email_service import send_password_reset_email
from app.core.security import get_password_hash
from app.core.logging import app_logger as logger


class PasswordResetService:
    """비밀번호 재설정 서비스"""

    @staticmethod
    def generate_reset_token() -> str:
        """
        비밀번호 재설정 토큰 생성

        Returns:
            32바이트 hex 토큰
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    async def request_password_reset(
        db: AsyncSession,
        email: str
    ) -> bool:
        """
        비밀번호 재설정 요청

        Args:
            db: 데이터베이스 세션
            email: 사용자 이메일

        Returns:
            요청 성공 여부 (보안상 항상 True 반환)
        """
        # 사용자 조회
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            # 보안상 사용자 존재 여부를 노출하지 않음
            logger.warning(f"존재하지 않는 이메일로 비밀번호 재설정 요청: {email}")
            return True

        # 재설정 토큰 생성
        reset_token = PasswordResetService.generate_reset_token()
        reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)  # 1시간 유효

        # 사용자 업데이트
        user.reset_token = reset_token
        user.reset_token_expires_at = reset_token_expires_at

        await db.commit()

        # 재설정 이메일 발송
        try:
            await send_password_reset_email(
                email=user.email,
                token=reset_token
            )
            logger.info(f"비밀번호 재설정 이메일 발송: {user.email}")
        except Exception as e:
            logger.error(f"비밀번호 재설정 이메일 발송 실패: {e}")

        return True

    @staticmethod
    async def verify_reset_token(
        db: AsyncSession,
        token: str
    ) -> Optional[User]:
        """
        재설정 토큰 검증

        Args:
            db: 데이터베이스 세션
            token: 재설정 토큰

        Returns:
            검증된 사용자 객체 (실패 시 None)
        """
        result = await db.execute(
            select(User).where(User.reset_token == token)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        # 토큰 만료 확인
        if not user.reset_token_expires_at:
            return None

        if datetime.utcnow() > user.reset_token_expires_at.replace(tzinfo=None):
            logger.warning(f"만료된 재설정 토큰 사용 시도: user_id={user.id}")
            return None

        return user

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        token: str,
        new_password: str
    ) -> bool:
        """
        비밀번호 재설정

        Args:
            db: 데이터베이스 세션
            token: 재설정 토큰
            new_password: 새 비밀번호

        Returns:
            재설정 성공 여부
        """
        # 토큰 검증
        user = await PasswordResetService.verify_reset_token(db, token)

        if not user:
            return False

        # 비밀번호 업데이트
        user.hashed_password = get_password_hash(new_password)

        # 토큰 무효화
        user.reset_token = None
        user.reset_token_expires_at = None

        await db.commit()

        logger.info(f"비밀번호 재설정 완료: user_id={user.id}")

        return True

    @staticmethod
    async def cancel_password_reset(
        db: AsyncSession,
        user: User
    ) -> bool:
        """
        비밀번호 재설정 취소 (토큰 무효화)

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체

        Returns:
            취소 성공 여부
        """
        if not user.reset_token:
            return False

        user.reset_token = None
        user.reset_token_expires_at = None

        await db.commit()

        logger.info(f"비밀번호 재설정 취소: user_id={user.id}")

        return True
