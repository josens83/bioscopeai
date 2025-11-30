"""
감사 로그 모델

중요한 사용자 활동 및 관리자 작업 추적
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    """
    감사 로그 모델

    보안 및 규정 준수를 위한 사용자 활동 추적
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 사용자 정보
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String, nullable=True)  # 사용자 삭제 시를 위한 백업
    email = Column(String, nullable=True)  # 사용자 삭제 시를 위한 백업

    # 작업 정보
    action = Column(String, nullable=False, index=True)  # 예: user.login, user.created, admin.user.suspended
    resource_type = Column(String, nullable=True, index=True)  # 예: user, subscription, paper
    resource_id = Column(String, nullable=True)  # 영향받은 리소스 ID

    # 상세 정보
    description = Column(Text, nullable=True)  # 사람이 읽을 수 있는 설명
    changes = Column(JSON, nullable=True)  # 변경 내용 (이전/이후 값)
    metadata = Column(JSON, nullable=True)  # 추가 메타데이터

    # 요청 정보
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # 결과
    status = Column(String, nullable=False, default="success")  # success, failure, error
    error_message = Column(Text, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 관계
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
