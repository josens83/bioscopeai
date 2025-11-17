"""
감사 로그 서비스

중요한 사용자 활동 및 관리자 작업 기록
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.models.user import User
from typing import Optional, Dict, Any
from fastapi import Request
from app.core.logging import app_logger as logger


class AuditService:
    """감사 로그 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ):
        """
        감사 로그 기록

        Args:
            action: 작업 (예: user.login, user.created, admin.user.suspended)
            user: User 객체 (선택)
            user_id: 사용자 ID (선택)
            resource_type: 리소스 타입 (예: user, subscription, paper)
            resource_id: 리소스 ID
            description: 사람이 읽을 수 있는 설명
            changes: 변경 내용 {"old": {...}, "new": {...}}
            metadata: 추가 메타데이터
            request: FastAPI Request 객체 (IP, User-Agent 추출용)
            status: 결과 (success, failure, error)
            error_message: 에러 메시지
        """
        try:
            # 사용자 정보
            if user:
                user_id = user.id
                username = user.username
                email = user.email
            else:
                username = None
                email = None

            # 요청 정보
            ip_address = None
            user_agent = None
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")

            # 감사 로그 생성
            audit_log = AuditLog(
                user_id=user_id,
                username=username,
                email=email,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                description=description,
                changes=changes,
                metadata=metadata,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                error_message=error_message,
            )

            self.db.add(audit_log)
            await self.db.commit()

            # 중요한 작업은 로그에도 기록
            if status == "success":
                logger.info(
                    f"[AUDIT] {action} - User: {username or user_id} - {description or 'No description'}",
                    extra={
                        "action": action,
                        "user_id": user_id,
                        "resource_type": resource_type,
                        "resource_id": resource_id,
                    },
                )
            else:
                logger.warning(
                    f"[AUDIT] {action} FAILED - User: {username or user_id} - {error_message or description}",
                    extra={
                        "action": action,
                        "user_id": user_id,
                        "status": status,
                        "error": error_message,
                    },
                )

        except Exception as e:
            # 감사 로그 기록 실패해도 메인 로직은 계속 진행
            logger.error(f"감사 로그 기록 실패: {e}", exc_info=True)


# 자주 사용되는 작업들을 위한 헬퍼 함수들

async def log_user_login(db: AsyncSession, user: User, request: Request, success: bool = True):
    """사용자 로그인 기록"""
    audit = AuditService(db)
    await audit.log(
        action="user.login",
        user=user,
        description=f"사용자 {user.username} 로그인 {'성공' if success else '실패'}",
        request=request,
        status="success" if success else "failure",
    )


async def log_user_created(db: AsyncSession, user: User, request: Request):
    """사용자 생성 기록"""
    audit = AuditService(db)
    await audit.log(
        action="user.created",
        user=user,
        resource_type="user",
        resource_id=user.id,
        description=f"새 사용자 계정 생성: {user.email}",
        request=request,
    )


async def log_user_updated(
    db: AsyncSession,
    user: User,
    changes: Dict[str, Any],
    request: Request,
):
    """사용자 정보 업데이트 기록"""
    audit = AuditService(db)
    await audit.log(
        action="user.updated",
        user=user,
        resource_type="user",
        resource_id=user.id,
        description=f"사용자 정보 업데이트: {', '.join(changes.get('new', {}).keys())}",
        changes=changes,
        request=request,
    )


async def log_password_changed(db: AsyncSession, user: User, request: Request):
    """비밀번호 변경 기록"""
    audit = AuditService(db)
    await audit.log(
        action="user.password_changed",
        user=user,
        resource_type="user",
        resource_id=user.id,
        description=f"사용자 {user.username} 비밀번호 변경",
        request=request,
    )


async def log_admin_action(
    db: AsyncSession,
    admin: User,
    action: str,
    target_user: User,
    description: str,
    request: Request,
    changes: Optional[Dict[str, Any]] = None,
):
    """관리자 작업 기록"""
    audit = AuditService(db)
    await audit.log(
        action=f"admin.{action}",
        user=admin,
        resource_type="user",
        resource_id=target_user.id,
        description=description,
        changes=changes,
        metadata={
            "admin_id": admin.id,
            "admin_username": admin.username,
            "target_user_id": target_user.id,
            "target_username": target_user.username,
        },
        request=request,
    )


async def log_subscription_change(
    db: AsyncSession,
    user: User,
    action: str,
    plan_name: str,
    description: str,
    request: Optional[Request] = None,
):
    """구독 변경 기록"""
    audit = AuditService(db)
    await audit.log(
        action=f"subscription.{action}",
        user=user,
        resource_type="subscription",
        description=description,
        metadata={"plan": plan_name},
        request=request,
    )
