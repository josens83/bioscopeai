"""
2단계 인증 (Two-Factor Authentication) API

TOTP 기반 보안 강화
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.two_factor_service import TwoFactorAuthService
from app.core.logging import app_logger as logger


router = APIRouter()


# ============================================================================
# Schemas
# ============================================================================

class Enable2FAResponse(BaseModel):
    """2FA 활성화 시작 응답"""
    secret: str = Field(..., description="TOTP 시크릿 (수동 입력용)")
    qr_code: str = Field(..., description="QR 코드 이미지 (Base64)")
    backup_codes: List[str] = Field(..., description="백업 코드 목록 (안전하게 보관 필요)")
    message: str = Field(..., description="안내 메시지")


class Verify2FARequest(BaseModel):
    """2FA 검증 요청"""
    token: str = Field(..., description="6자리 TOTP 코드", min_length=6, max_length=6)


class Disable2FARequest(BaseModel):
    """2FA 비활성화 요청"""
    password: str = Field(..., description="현재 비밀번호 (확인용)")


class TwoFactorStatusResponse(BaseModel):
    """2FA 상태 응답"""
    enabled: bool = Field(..., description="2FA 활성화 여부")
    backup_codes_remaining: Optional[int] = Field(None, description="남은 백업 코드 개수")


# ============================================================================
# 엔드포인트
# ============================================================================

@router.post("/enable", response_model=Enable2FAResponse)
async def enable_2fa(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    2단계 인증 활성화 시작

    QR 코드와 백업 코드를 반환합니다.
    사용자는 authenticator 앱으로 QR 코드를 스캔하고,
    다음 단계에서 생성된 코드로 검증해야 합니다.

    **중요**: 백업 코드는 안전한 곳에 보관하세요!
    """
    secret, qr_code, backup_codes = await TwoFactorAuthService.enable_2fa(db, current_user)

    return Enable2FAResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes,
        message="Authenticator 앱으로 QR 코드를 스캔하고, 생성된 6자리 코드로 검증을 완료하세요. 백업 코드는 안전한 곳에 보관하세요."
    )


@router.post("/verify")
async def verify_and_activate_2fa(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    2FA 검증 및 활성화

    Authenticator 앱에서 생성된 6자리 코드를 입력하여
    2FA 설정을 완료합니다.
    """
    success = await TwoFactorAuthService.verify_and_activate_2fa(
        db, current_user, request.token
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 인증 코드입니다. 다시 시도해주세요."
        )

    logger.info(f"2FA 활성화 완료: user_id={current_user.id}")

    return {
        "message": "2단계 인증이 성공적으로 활성화되었습니다.",
        "enabled": True
    }


@router.post("/disable")
async def disable_2fa(
    request: Disable2FARequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    2FA 비활성화

    보안을 위해 현재 비밀번호 확인이 필요합니다.
    """
    success = await TwoFactorAuthService.disable_2fa(
        db, current_user, request.password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 올바르지 않거나 2FA가 활성화되어 있지 않습니다."
        )

    logger.info(f"2FA 비활성화: user_id={current_user.id}")

    return {
        "message": "2단계 인증이 비활성화되었습니다.",
        "enabled": False
    }


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    2FA 활성화 상태 확인

    현재 사용자의 2FA 설정 상태를 조회합니다.
    """
    enabled = await TwoFactorAuthService.check_2fa_required(db, current_user)
    backup_codes_count = None

    if enabled:
        backup_codes_count = await TwoFactorAuthService.get_remaining_backup_codes(
            db, current_user
        )

    return TwoFactorStatusResponse(
        enabled=enabled,
        backup_codes_remaining=backup_codes_count
    )


@router.get("/backup-codes/count")
async def get_backup_codes_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    남은 백업 코드 개수 조회

    백업 코드는 일회용이므로, 사용할 때마다 줄어듭니다.
    """
    count = await TwoFactorAuthService.get_remaining_backup_codes(db, current_user)

    return {
        "backup_codes_remaining": count,
        "warning": "백업 코드가 5개 미만이면 2FA를 재설정하여 새 백업 코드를 발급받으세요." if count < 5 else None
    }
