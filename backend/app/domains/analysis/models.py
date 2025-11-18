"""
Analysis Domain Models
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AnalysisType(str, enum.Enum):
    """분석 타입"""
    SUMMARY = "summary"
    COMPARISON = "comparison"
    QA = "qa"
    TREND = "trend"


class Analysis(Base):
    """분석 결과 모델"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)

    # 분석 정보
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    query = Column(Text, nullable=True)
    result = Column(JSON, nullable=False)

    # 비교 분석의 경우 여러 논문 ID
    compared_paper_ids = Column(JSON, nullable=True)

    # 메타 정보
    processing_time = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계
    user = relationship("User", back_populates="analyses")
    paper = relationship("Paper", back_populates="analyses")
