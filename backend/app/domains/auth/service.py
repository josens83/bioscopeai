"""
Auth Domain Service - 비즈니스 로직
"""
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.shared.infrastructure.email.templates import send_verification_email, send_password_reset_email, send_welcome_email
from app.services.audit_service import log_user_created, log_user_login, log_password_changed
from .models import User
from .schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from .exceptions import (
    InvalidCredentialsException,
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    UserNotFoundException,
    InvalidTokenException,
)


class AuthService:
    """인증 서비스 - 회원가입, 로그인, 이메일 인증 등"""

    @staticmethod
    async def register(db: AsyncSession, user_in: UserCreate) -> User:
        """사용자 등록"""
        # 이메일 중복 확인
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise EmailAlreadyExistsException()

        # 사용자명 중복 확인
        result = await db.execute(select(User).where(User.username == user_in.username))
        if result.scalar_one_or_none():
            raise UsernameAlreadyExistsException()

        # 이메일 인증 토큰 생성
        verification_token = secrets.token_urlsafe(32)

        # 사용자 생성
        user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            verification_token=verification_token,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # 감사 로그
        await log_user_created(db, user.id, user.email)

        # 인증 이메일 전송
        await send_verification_email(user.email, verification_token)

        # 환영 이메일 전송
        await send_welcome_email(user.email, user.username)

        return user

    @staticmethod
    async def login(db: AsyncSession, credentials: UserLogin) -> TokenResponse:
        """로그인"""
        # 사용자 조회
        result = await db.execute(select(User).where(User.email == credentials.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsException()

        # 토큰 생성
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # 감사 로그
        await log_user_login(db, user.id, user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    async def verify_email(db: AsyncSession, token: str) -> User:
        """이메일 인증"""
        result = await db.execute(select(User).where(User.verification_token == token))
        user = result.scalar_one_or_none()

        if not user:
            raise InvalidTokenException()

        user.is_verified = True
        user.verified_at = datetime.utcnow()
        user.verification_token = None

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str) -> bool:
        """비밀번호 재설정 요청"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        # 보안: 사용자 존재 여부를 노출하지 않음
        if not user:
            return True

        # 토큰 생성
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)

        await db.commit()

        # 이메일 전송
        await send_password_reset_email(email, reset_token)

        return True

    @staticmethod
    async def reset_password(db: AsyncSession, token: str, new_password: str) -> User:
        """비밀번호 재설정"""
        result = await db.execute(select(User).where(User.reset_token == token))
        user = result.scalar_one_or_none()

        if not user:
            raise InvalidTokenException()

        # 토큰 만료 확인
        if user.reset_token_expires_at < datetime.utcnow():
            raise InvalidTokenException()

        # 비밀번호 변경
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires_at = None

        await db.commit()
        await db.refresh(user)

        # 감사 로그
        await log_password_changed(db, user.id, user.email)

        return user

    @staticmethod
    async def resend_verification_email(db: AsyncSession, email: str) -> bool:
        """인증 이메일 재전송"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundException()

        if user.is_verified:
            return True

        # 새 토큰 생성
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token

        await db.commit()

        # 이메일 재전송
        await send_verification_email(email, verification_token)

        return True
