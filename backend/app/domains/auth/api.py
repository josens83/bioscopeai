"""
Auth Domain API Router
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rate_limiting import limiter, RateLimits
from .dependencies import get_db, get_current_user
from .service import AuthService
from .schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
)
from .models import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH)
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    사용자 등록

    - 이메일 중복 확인
    - 사용자명 중복 확인
    - 비밀번호 해시화 저장
    - 이메일 인증 토큰 생성 및 발송
    - 환영 이메일 발송
    """
    user = await AuthService.register(db, user_in)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit(RateLimits.AUTH)
async def login(request: Request, credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    로그인

    - 이메일/비밀번호 검증
    - JWT 액세스 토큰 생성 (30분)
    - JWT 리프레시 토큰 생성 (7일)
    - 감사 로그 기록
    """
    return await AuthService.login(db, credentials)


@router.post("/verify-email")
@limiter.limit(RateLimits.AUTH)
async def verify_email(request: Request, verification: EmailVerification, db: AsyncSession = Depends(get_db)):
    """
    이메일 인증

    - 인증 토큰 검증
    - is_verified = True 업데이트
    - verified_at 타임스탬프 기록
    """
    user = await AuthService.verify_email(db, verification.token)
    return {"message": "이메일 인증이 완료되었습니다", "email": user.email}


@router.post("/resend-verification")
@limiter.limit("3/hour")  # 시간당 3회 제한
async def resend_verification_email(request: Request, email_request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """
    이메일 인증 재전송

    - 새 인증 토큰 생성
    - 인증 이메일 재발송
    """
    await AuthService.resend_verification_email(db, email_request.email)
    return {"message": "인증 이메일이 재전송되었습니다"}


@router.post("/password-reset/request")
@limiter.limit("3/hour")
async def request_password_reset(request: Request, email_request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """
    비밀번호 재설정 요청

    - 재설정 토큰 생성 (1시간 유효)
    - 재설정 이메일 발송
    - 보안: 사용자 존재 여부 노출 안 함
    """
    await AuthService.request_password_reset(db, email_request.email)
    return {"message": "비밀번호 재설정 이메일이 전송되었습니다"}


@router.post("/password-reset/confirm")
@limiter.limit(RateLimits.AUTH)
async def reset_password(request: Request, reset_data: PasswordReset, db: AsyncSession = Depends(get_db)):
    """
    비밀번호 재설정 확인

    - 재설정 토큰 검증
    - 토큰 만료 확인
    - 새 비밀번호 해시화 저장
    - 감사 로그 기록
    """
    user = await AuthService.reset_password(db, reset_data.token, reset_data.new_password)
    return {"message": "비밀번호가 재설정되었습니다", "email": user.email}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    현재 사용자 정보 조회

    - JWT 토큰 검증
    - 사용자 정보 반환
    """
    return current_user


@router.post("/refresh")
@limiter.limit(RateLimits.AUTH)
async def refresh_token(request: Request, credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    토큰 갱신

    - 리프레시 토큰 검증
    - 새 액세스 토큰 발급
    """
    # TODO: 리프레시 토큰 전용 로직 구현
    return await AuthService.login(db, credentials)
