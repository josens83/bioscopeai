"""
사용량 추적 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Usage(Base):
    """사용자별 월별 사용량 추적"""

    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 사용량 카운터
    papers_analyzed = Column(Integer, default=0, nullable=False)  # 분석한 논문 수
    rag_queries = Column(Integer, default=0, nullable=False)  # RAG 쿼리 수
    api_calls = Column(Integer, default=0, nullable=False)  # 전체 API 호출 수

    # 기간 (월별)
    year = Column(Integer, nullable=False)  # 2024
    month = Column(Integer, nullable=False)  # 1-12

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계
    user = relationship("User", back_populates="usages")

    # 복합 인덱스: 사용자 + 연도 + 월 (unique)
    __table_args__ = (
        Index('ix_usage_user_year_month', 'user_id', 'year', 'month', unique=True),
    )


class PlanLimit(Base):
    """플랜별 사용량 제한 설정"""

    __tablename__ = "plan_limits"

    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String, unique=True, nullable=False, index=True)  # free, basic, pro

    # 월별 제한
    papers_per_month = Column(Integer, nullable=False)  # -1 = unlimited
    rag_queries_per_month = Column(Integer, nullable=False)  # -1 = unlimited
    api_calls_per_day = Column(Integer, nullable=False)  # Rate limit

    # 기능 제한
    max_file_size_mb = Column(Integer, default=10, nullable=False)  # MB
    pdf_export = Column(Integer, default=0, nullable=False)  # 0=불가, 1=가능
    priority_support = Column(Integer, default=0, nullable=False)  # 0=불가, 1=가능

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
