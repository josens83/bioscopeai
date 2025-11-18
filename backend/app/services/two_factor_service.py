"""
2단계 인증 (Two-Factor Authentication) 서비스

TOTP 기반 2FA 설정 및 검증
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Tuple
import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
import json
from datetime import datetime

from app.models.user import User
from app.models.two_factor_auth import TwoFactorAuth
from app.core.config import settings
from app.core.logging import app_logger as logger


class TwoFactorAuthService:
    """2단계 인증 서비스"""

    @staticmethod
    def generate_secret() -> str:
        """
        TOTP 시크릿 생성

        Returns:
            Base32 인코딩된 시크릿
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_totp(secret: str) -> pyotp.TOTP:
        """
        TOTP 객체 생성

        Args:
            secret: Base32 인코딩된 시크릿

        Returns:
            TOTP 객체
        """
        return pyotp.TOTP(secret)

    @staticmethod
    def generate_qr_code(secret: str, user_email: str, issuer: str = "BioscopeAI") -> str:
        """
        QR 코드 생성 (Base64 인코딩된 이미지)

        Args:
            secret: Base32 인코딩된 시크릿
            user_email: 사용자 이메일
            issuer: 발급자 이름

        Returns:
            Base64 인코딩된 QR 코드 이미지
        """
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )

        # QR 코드 생성
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # 이미지를 Base64로 인코딩
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """
        TOTP 토큰 검증

        Args:
            secret: Base32 인코딩된 시크릿
            token: 사용자가 입력한 6자리 코드

        Returns:
            검증 성공 여부
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # 30초 윈도우 허용

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        백업 코드 생성

        Args:
            count: 생성할 백업 코드 개수

        Returns:
            백업 코드 목록
        """
        codes = []
        for _ in range(count):
            # 8자리 랜덤 코드 생성
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        백업 코드 해싱

        Args:
            code: 백업 코드

        Returns:
            해시된 코드
        """
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    async def enable_2fa(
        db: AsyncSession,
        user: User
    ) -> Tuple[str, str, List[str]]:
        """
        2FA 활성화 시작 (시크릿 생성 및 QR 코드 반환)

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체

        Returns:
            (시크릿, QR 코드 이미지, 백업 코드 목록)
        """
        # 기존 2FA 설정 확인
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        existing_2fa = result.scalar_one_or_none()

        # 새 시크릿 생성
        secret = TwoFactorAuthService.generate_secret()
        qr_code = TwoFactorAuthService.generate_qr_code(secret, user.email)

        # 백업 코드 생성
        backup_codes = TwoFactorAuthService.generate_backup_codes()
        hashed_codes = [TwoFactorAuthService.hash_backup_code(code) for code in backup_codes]

        if existing_2fa:
            # 기존 설정 업데이트
            existing_2fa.secret = secret
            existing_2fa.is_enabled = False  # 검증 완료 전까지 비활성화
            existing_2fa.is_verified = False
            existing_2fa.backup_codes = json.dumps(hashed_codes)
        else:
            # 새 설정 생성
            new_2fa = TwoFactorAuth(
                user_id=user.id,
                secret=secret,
                is_enabled=False,
                is_verified=False,
                backup_codes=json.dumps(hashed_codes),
            )
            db.add(new_2fa)

        await db.commit()

        logger.info(f"2FA 활성화 시작: user_id={user.id}")

        return secret, qr_code, backup_codes

    @staticmethod
    async def verify_and_activate_2fa(
        db: AsyncSession,
        user: User,
        token: str
    ) -> bool:
        """
        2FA 검증 및 활성화

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체
            token: TOTP 토큰

        Returns:
            활성화 성공 여부
        """
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_fa = result.scalar_one_or_none()

        if not two_fa:
            return False

        # TOTP 검증
        if not TwoFactorAuthService.verify_totp(two_fa.secret, token):
            return False

        # 활성화
        two_fa.is_enabled = True
        two_fa.is_verified = True
        two_fa.enabled_at = datetime.utcnow()

        await db.commit()

        logger.info(f"2FA 활성화 완료: user_id={user.id}")

        return True

    @staticmethod
    async def disable_2fa(
        db: AsyncSession,
        user: User,
        password: str  # 보안을 위해 비밀번호 확인 필요
    ) -> bool:
        """
        2FA 비활성화

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체
            password: 사용자 비밀번호 (확인용)

        Returns:
            비활성화 성공 여부
        """
        from app.core.security import verify_password

        # 비밀번호 확인
        if not verify_password(password, user.hashed_password):
            return False

        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_fa = result.scalar_one_or_none()

        if not two_fa:
            return False

        # 삭제
        await db.delete(two_fa)
        await db.commit()

        logger.info(f"2FA 비활성화: user_id={user.id}")

        return True

    @staticmethod
    async def verify_2fa_login(
        db: AsyncSession,
        user: User,
        token: str
    ) -> bool:
        """
        로그인 시 2FA 검증

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체
            token: TOTP 토큰 또는 백업 코드

        Returns:
            검증 성공 여부
        """
        result = await db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.user_id == user.id,
                TwoFactorAuth.is_enabled == True
            )
        )
        two_fa = result.scalar_one_or_none()

        if not two_fa:
            return False

        # TOTP 토큰 검증 시도
        if TwoFactorAuthService.verify_totp(two_fa.secret, token):
            return True

        # 백업 코드 검증 시도
        if two_fa.backup_codes:
            try:
                backup_codes = json.loads(two_fa.backup_codes)
                hashed_token = TwoFactorAuthService.hash_backup_code(token.upper())

                if hashed_token in backup_codes:
                    # 사용된 백업 코드 제거
                    backup_codes.remove(hashed_token)
                    two_fa.backup_codes = json.dumps(backup_codes)
                    await db.commit()

                    logger.info(f"백업 코드 사용: user_id={user.id}")
                    return True
            except json.JSONDecodeError:
                pass

        return False

    @staticmethod
    async def check_2fa_required(
        db: AsyncSession,
        user: User
    ) -> bool:
        """
        사용자가 2FA를 활성화했는지 확인

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체

        Returns:
            2FA 필요 여부
        """
        result = await db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.user_id == user.id,
                TwoFactorAuth.is_enabled == True
            )
        )
        two_fa = result.scalar_one_or_none()

        return two_fa is not None

    @staticmethod
    async def get_remaining_backup_codes(
        db: AsyncSession,
        user: User
    ) -> int:
        """
        남은 백업 코드 개수 조회

        Args:
            db: 데이터베이스 세션
            user: 사용자 객체

        Returns:
            남은 백업 코드 개수
        """
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_fa = result.scalar_one_or_none()

        if not two_fa or not two_fa.backup_codes:
            return 0

        try:
            backup_codes = json.loads(two_fa.backup_codes)
            return len(backup_codes)
        except json.JSONDecodeError:
            return 0
