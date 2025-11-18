"""
2단계 인증 (Two-Factor Authentication) 모델

TOTP 기반 2FA 보안 강화
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class TwoFactorAuth(Base):
    """2단계 인증 설정"""
    __tablename__ = "two_factor_auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # TOTP 설정
    secret = Column(String, nullable=False)  # Base32 인코딩된 시크릿
    is_enabled = Column(Boolean, default=False, nullable=False)  # 2FA 활성화 여부
    is_verified = Column(Boolean, default=False, nullable=False)  # 초기 설정 완료 여부

    # 백업 코드 (복구용)
    backup_codes = Column(String, nullable=True)  # JSON array of hashed backup codes

    # 메타데이터
    enabled_at = Column(DateTime(timezone=True), nullable=True)  # 활성화 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 관계
    user = relationship("User", back_populates="two_factor_auth")

    def __repr__(self):
        return f"<TwoFactorAuth(user_id={self.user_id}, is_enabled={self.is_enabled})>"
