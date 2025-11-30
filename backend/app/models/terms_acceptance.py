"""
이용약관/개인정보 처리방침 동의 모델

법적 규정 준수를 위한 약관 동의 관리
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class TermsAcceptance(Base):
    """약관 동의 기록"""
    __tablename__ = "terms_acceptances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 약관 정보
    terms_type = Column(String, nullable=False, index=True)  # "terms_of_service", "privacy_policy", "marketing"
    version = Column(String, nullable=False)  # 약관 버전 (예: "1.0.0", "2024-01-15")

    # 동의 정보
    accepted = Column(Boolean, default=False, nullable=False)  # 동의 여부
    accepted_at = Column(DateTime(timezone=True), nullable=True)  # 동의 시각
    ip_address = Column(String, nullable=True)  # 동의 시 IP 주소 (법적 증거)
    user_agent = Column(Text, nullable=True)  # 동의 시 User Agent

    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 관계
    user = relationship("User", back_populates="terms_acceptances")

    def __repr__(self):
        return f"<TermsAcceptance(user_id={self.user_id}, type={self.terms_type}, version={self.version}, accepted={self.accepted})>"


class TermsVersion(Base):
    """약관 버전 관리"""
    __tablename__ = "terms_versions"

    id = Column(Integer, primary_key=True, index=True)

    # 약관 식별
    terms_type = Column(String, nullable=False, index=True)  # "terms_of_service", "privacy_policy"
    version = Column(String, nullable=False)  # 버전 번호
    language = Column(String, default="ko", nullable=False)  # 언어 (ko, en)

    # 약관 내용
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # 마크다운 또는 HTML

    # 상태
    is_active = Column(Boolean, default=True, nullable=False)  # 현재 활성 버전인지
    is_required = Column(Boolean, default=True, nullable=False)  # 필수 동의인지

    # 메타데이터
    effective_date = Column(DateTime(timezone=True), nullable=False)  # 시행일
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 작성자 (관리자)

    def __repr__(self):
        return f"<TermsVersion(type={self.terms_type}, version={self.version}, active={self.is_active})>"
