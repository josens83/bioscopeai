"""
사용자 프로필 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.api.deps import get_db, get_current_user, get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.core.security import verify_password, get_password_hash
from app.services.audit_service import log_user_updated, log_password_changed, AuditService
from app.core.logging import app_logger as logger

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """현재 로그인한 사용자 프로필 조회"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    request: Request,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 프로필 업데이트"""
    # 변경 사항 추적
    changes = {"old": {}, "new": {}}

    # 이메일 변경 시 중복 확인
    if user_update.email and user_update.email != current_user.email:
        result = await db.execute(
            select(User).where(User.email == user_update.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다",
            )
        changes["old"]["email"] = current_user.email
        changes["new"]["email"] = user_update.email
        current_user.email = user_update.email
        # 이메일 변경 시 재인증 필요
        current_user.is_verified = False
        logger.info(f"사용자 이메일 변경: {current_user.id} -> {user_update.email}")

    # 사용자명 변경 시 중복 확인
    if user_update.username and user_update.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == user_update.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 사용자명입니다",
            )
        changes["old"]["username"] = current_user.username
        changes["new"]["username"] = user_update.username
        current_user.username = user_update.username

    # 기타 정보 업데이트
    if user_update.full_name is not None:
        changes["old"]["full_name"] = current_user.full_name
        changes["new"]["full_name"] = user_update.full_name
        current_user.full_name = user_update.full_name

    await db.commit()
    await db.refresh(current_user)

    # 감사 로그 기록
    if changes["new"]:  # 실제 변경사항이 있는 경우만
        await log_user_updated(db, current_user, changes, request)

    logger.info(f"사용자 프로필 업데이트: {current_user.id}")
    return current_user


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: Request,
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """비밀번호 변경"""
    # 현재 비밀번호 확인
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다",
        )

    # 새 비밀번호와 현재 비밀번호가 같은지 확인
    if password_change.current_password == password_change.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호는 현재 비밀번호와 달라야 합니다",
        )

    # 비밀번호 업데이트
    current_user.hashed_password = get_password_hash(password_change.new_password)
    await db.commit()

    # 감사 로그 기록
    await log_password_changed(db, current_user, request)

    logger.info(f"비밀번호 변경 완료: {current_user.id}")
    return {"message": "비밀번호가 성공적으로 변경되었습니다"}


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_user_account(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 계정 삭제 (소프트 삭제)"""
    # 소프트 삭제 (비활성화)
    current_user.is_active = False
    await db.commit()

    # 감사 로그 기록
    audit = AuditService(db)
    await audit.log(
        action="user.deleted",
        user=current_user,
        resource_type="user",
        resource_id=current_user.id,
        description=f"사용자 계정 삭제 (소프트): {current_user.email}",
        request=request,
    )

    logger.warning(f"사용자 계정 삭제: {current_user.id} ({current_user.email})")
    return {"message": "계정이 성공적으로 삭제되었습니다"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """특정 사용자 정보 조회 (본인 또는 관리자만)"""
    # 본인 정보이거나 관리자인 경우만 허용
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )

    return user
