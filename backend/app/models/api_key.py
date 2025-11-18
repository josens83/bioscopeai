"""
API 키 모델

개발자 API 접근을 위한 API 키 관리
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class APIKey(Base):
    """API 키 모델 - 프로그래밍 방식의 API 접근"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # API 키 정보
    name = Column(String, nullable=False)  # 키 이름 (예: "Production Server", "Development")
    key = Column(String, unique=True, nullable=False, index=True)  # 실제 API 키 (해시됨)
    prefix = Column(String, nullable=False)  # 키 프리픽스 (표시용, 예: "bsa_abc...")

    # 권한 및 제한
    scopes = Column(Text, nullable=True)  # 권한 범위 (JSON array: ["papers:read", "analysis:write"])
    rate_limit = Column(Integer, nullable=True)  # 분당 요청 제한 (없으면 플랜 기본값 사용)

    # 상태
    is_active = Column(Boolean, default=True, nullable=False)

    # 사용 통계
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)  # 총 사용 횟수

    # 보안
    ip_whitelist = Column(Text, nullable=True)  # IP 화이트리스트 (JSON array)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # 만료 날짜 (없으면 무제한)

    # 메타데이터
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 관계
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.name}, user_id={self.user_id}, prefix={self.prefix})>"

    @property
    def is_expired(self) -> bool:
        """API 키가 만료되었는지 확인"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)

    @property
    def is_valid(self) -> bool:
        """API 키가 유효한지 확인 (활성화 + 미만료)"""
        return self.is_active and not self.is_expired
