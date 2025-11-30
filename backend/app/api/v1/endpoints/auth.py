from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, PasswordResetRequest, PasswordReset, EmailVerification
from app.services.email_service import send_password_reset_email, send_verification_email, send_welcome_email
from app.services.audit_service import log_user_created, log_user_login, log_password_changed
from datetime import datetime, timedelta
import secrets
from app.core.logging import app_logger as logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """사용자 등록"""
    # 이메일 중복 확인
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다",
        )

    # 사용자명 중복 확인
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다",
        )

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

    # 감사 로그 기록
    await log_user_created(db, user, request)

    # 환영 이메일 및 인증 이메일 전송
    try:
        await send_welcome_email(user.email, user.username)
        await send_verification_email(user.email, verification_token)
        logger.info(f"가입 완료 및 이메일 전송: {user.email}")
    except Exception as e:
        logger.error(f"가입 이메일 전송 실패: {e}")
        # 이메일 전송 실패해도 가입은 완료

    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """로그인"""
    # 사용자 조회
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다",
        )

    # 토큰 생성
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 감사 로그 기록
    await log_user_login(db, user, request)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
@limiter.limit("3/hour")
async def request_password_reset(request: Request, data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """비밀번호 재설정 이메일 요청"""
    # 사용자 조회
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # 보안상 사용자 존재 여부와 관계없이 동일한 응답 반환
    if user and user.is_active:
        # 재설정 토큰 생성 (안전한 랜덤 토큰)
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)

        await db.commit()

        # 이메일 전송
        try:
            await send_password_reset_email(user.email, reset_token)
            logger.info(f"비밀번호 재설정 이메일 전송: {user.email}")
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
            # 에러가 발생해도 사용자에게는 성공 메시지 반환 (보안)

    return {"message": "비밀번호 재설정 이메일을 전송했습니다. 이메일을 확인해주세요."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/hour")
async def reset_password(request: Request, data: PasswordReset, db: AsyncSession = Depends(get_db)):
    """비밀번호 재설정"""
    # 토큰으로 사용자 조회
    result = await db.execute(
        select(User).where(
            User.reset_token == data.token,
            User.reset_token_expires_at > datetime.utcnow()
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않거나 만료된 토큰입니다",
        )

    # 비밀번호 업데이트
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None

    await db.commit()

    # 감사 로그 기록
    await log_password_changed(db, user, request)

    logger.info(f"비밀번호 재설정 완료: {user.email}")

    return {"message": "비밀번호가 성공적으로 재설정되었습니다."}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def verify_email(request: Request, data: EmailVerification, db: AsyncSession = Depends(get_db)):
    """이메일 인증"""
    # 토큰으로 사용자 조회
    result = await db.execute(
        select(User).where(User.verification_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 인증 토큰입니다",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 인증된 계정입니다",
        )

    # 이메일 인증 처리
    user.is_verified = True
    user.verified_at = datetime.utcnow()
    user.verification_token = None

    await db.commit()

    logger.info(f"이메일 인증 완료: {user.email}")

    return {"message": "이메일 인증이 완료되었습니다."}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
@limiter.limit("3/hour")
async def resend_verification(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """이메일 인증 재전송"""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 인증된 계정입니다",
        )

    # 새로운 인증 토큰 생성
    verification_token = secrets.token_urlsafe(32)
    current_user.verification_token = verification_token

    await db.commit()

    # 인증 이메일 전송
    try:
        await send_verification_email(current_user.email, verification_token)
        logger.info(f"인증 이메일 재전송: {current_user.email}")
    except Exception as e:
        logger.error(f"이메일 전송 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이메일 전송에 실패했습니다. 잠시 후 다시 시도해주세요.",
        )

    return {"message": "인증 이메일을 재전송했습니다. 이메일을 확인해주세요."}
