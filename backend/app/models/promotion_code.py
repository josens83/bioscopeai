"""
프로모션 코드/쿠폰 모델

마케팅 및 판촉 활동을 위한 할인 코드 관리
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, func
from app.core.database import Base
from datetime import datetime


class PromotionCode(Base):
    """프로모션 코드 모델"""
    __tablename__ = "promotion_codes"

    id = Column(Integer, primary_key=True, index=True)

    # 코드 정보
    code = Column(String, unique=True, nullable=False, index=True)  # 프로모션 코드 (예: "WELCOME2024")
    description = Column(Text, nullable=True)  # 코드 설명

    # 할인 정보
    discount_type = Column(String, nullable=False)  # "percentage" 또는 "fixed"
    discount_value = Column(Float, nullable=False)  # 할인율(%) 또는 할인금액($)

    # 제한 조건
    max_uses = Column(Integer, nullable=True)  # 최대 사용 횟수 (null=무제한)
    max_uses_per_user = Column(Integer, default=1, nullable=False)  # 사용자당 최대 사용 횟수
    min_purchase_amount = Column(Float, nullable=True)  # 최소 구매 금액

    # 적용 범위
    applicable_plans = Column(Text, nullable=True)  # 적용 가능한 플랜 (JSON array)

    # 유효 기간
    valid_from = Column(DateTime(timezone=True), nullable=False)  # 시작일
    valid_until = Column(DateTime(timezone=True), nullable=True)  # 종료일 (null=무기한)

    # 상태
    is_active = Column(Boolean, default=True, nullable=False)

    # 사용 통계
    uses_count = Column(Integer, default=0, nullable=False)  # 현재까지 사용 횟수

    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)  # 생성자 (관리자 ID)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PromotionCode(code={self.code}, discount={self.discount_value}{self.discount_type})>"

    @property
    def is_valid(self) -> bool:
        """코드가 현재 유효한지 확인"""
        if not self.is_active:
            return False

        now = datetime.utcnow()

        # 시작일 확인
        if self.valid_from and now < self.valid_from.replace(tzinfo=None):
            return False

        # 종료일 확인
        if self.valid_until and now > self.valid_until.replace(tzinfo=None):
            return False

        # 사용 횟수 확인
        if self.max_uses and self.uses_count >= self.max_uses:
            return False

        return True


class PromotionCodeUsage(Base):
    """프로모션 코드 사용 기록"""
    __tablename__ = "promotion_code_usages"

    id = Column(Integer, primary_key=True, index=True)

    # 프로모션 코드 정보
    promotion_code_id = Column(Integer, nullable=False, index=True)
    code = Column(String, nullable=False)  # 백업용

    # 사용자 정보
    user_id = Column(Integer, nullable=False, index=True)

    # 사용 정보
    subscription_id = Column(Integer, nullable=True)  # 적용된 구독 ID
    discount_applied = Column(Float, nullable=False)  # 실제 적용된 할인 금액

    # 메타데이터
    used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String, nullable=True)

    def __repr__(self):
        return f"<PromotionCodeUsage(code={self.code}, user_id={self.user_id}, discount={self.discount_applied})>"
